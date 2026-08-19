import asyncio
import hmac
import logging
from time import perf_counter
from urllib.parse import parse_qs

from starlette.responses import JSONResponse

from app.mcp.context import MCPRequestContext, request_context
from app.modules.mcp import service as mcp_management
from app.redis_client import redis_client

logger = logging.getLogger("yeyi.mcp")


def _header(scope: dict, name: str) -> str | None:
    wanted = name.lower().encode()
    for key, value in scope.get("headers", []):
        if key.lower() == wanted:
            return value.decode("latin-1")
    return None


def _query(scope: dict, name: str) -> str | None:
    values = parse_qs((scope.get("query_string") or b"").decode("utf-8", "ignore")).get(name)
    return values[0] if values else None


def _allowed(value: str | None, allowed: list[str], *, origin: bool = False) -> bool:
    if not allowed:
        return True
    if not value:
        return False
    normalized = value.rstrip("/").lower() if origin else value.rsplit(":", 1)[0].lower()
    return any(item == "*" or item.rstrip("/").lower() == normalized for item in allowed)


async def _write_audit(**kwargs) -> None:
    try:
        await asyncio.wait_for(mcp_management.record_request_log(**kwargs), timeout=1.0)
    except Exception:
        logger.warning("mcp_audit_log_write_failed")


def _schedule_audit(**kwargs) -> None:
    try:
        asyncio.create_task(_write_audit(**kwargs))
    except RuntimeError:
        logger.warning("mcp_audit_log_task_not_scheduled")


def _key_kwargs(key) -> dict:
    return {
        "key_id": key.id if key else None,
        "key_name": key.name if key else None,
        "key_fingerprint": key.fingerprint if key else None,
    }


class MCPAuthRateLimitMiddleware:
    """Authenticate MCP requests and enforce the current database-backed limits."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("path") not in {"/mcp", "/mcp/"}:
            await self.app(scope, receive, send)
            return

        started = perf_counter()
        client = scope.get("client") or ("unknown", 0)
        context = MCPRequestContext(
            client_ip=_header(scope, "x-real-ip") or client[0],
            user_agent=_header(scope, "user-agent"),
        )
        token = request_context.set(context)
        try:
            runtime = await mcp_management.get_runtime_settings()
            provided_key = _query(scope, "tavilyApiKey") or _query(scope, "api_key") or _header(scope, "x-mcp-api-key")
            matched_key = next(
                (key for key in runtime.keys if provided_key and hmac.compare_digest(provided_key, key.api_key)),
                None,
            )
            if not runtime.enabled:
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=503,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="MCP service is disabled",
                    **_key_kwargs(matched_key),
                )
                await JSONResponse({"detail": "MCP service is disabled"}, status_code=503)(scope, receive, send)
                return

            host = _header(scope, "host")
            origin = _header(scope, "origin")
            if not _allowed(host, runtime.allowed_hosts):
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=403,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="Host is not allowed",
                    **_key_kwargs(matched_key),
                )
                await JSONResponse({"detail": "Host is not allowed"}, status_code=403)(scope, receive, send)
                return
            if origin is not None and not _allowed(origin, runtime.allowed_origins, origin=True):
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=403,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="Origin is not allowed",
                    **_key_kwargs(matched_key),
                )
                await JSONResponse({"detail": "Origin is not allowed"}, status_code=403)(scope, receive, send)
                return

            if not matched_key:
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=401,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="Invalid MCP API key",
                    **_key_kwargs(None),
                )
                await JSONResponse({"detail": "Invalid MCP API key"}, status_code=401)(scope, receive, send)
                return

            context.api_key_id = matched_key.id
            context.api_key_name = matched_key.name
            context.api_key_fingerprint = matched_key.fingerprint
            try:
                await mcp_management.record_api_key_usage(matched_key.id)
            except Exception:
                logger.warning("mcp_api_key_usage_update_failed")
            rate_key = f"mcp_rate:{matched_key.fingerprint}:{context.client_ip or 'unknown'}"
            script = (
                "local current = redis.call('INCR', KEYS[1]); "
                "if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]); end; "
                "return current"
            )
            try:
                current = int(await redis_client.eval(script, 1, rate_key, runtime.rate_window))
            except Exception:
                logger.exception("mcp_rate_limit_unavailable")
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=503,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="MCP rate limiter unavailable",
                    **_key_kwargs(matched_key),
                )
                await JSONResponse({"detail": "MCP rate limiter unavailable"}, status_code=503)(scope, receive, send)
                return
            if current > runtime.rate_limit:
                _schedule_audit(
                    request_id=context.request_id, client_ip=context.client_ip, user_agent=context.user_agent,
                    rpc_method="transport", tool_name=None, success=False, http_status=429,
                    duration_ms=int((perf_counter() - started) * 1000), error_message="MCP rate limit exceeded",
                    **_key_kwargs(matched_key),
                )
                await JSONResponse({"detail": "MCP rate limit exceeded"}, status_code=429)(scope, receive, send)
                return

            await self.app(scope, receive, send)
        finally:
            request_context.reset(token)
