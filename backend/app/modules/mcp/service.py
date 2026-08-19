import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.modules.mcp.model import MCPApiKey, MCPRequestLog, MCPServiceSettings
from app.modules.mcp.schema import MCPApiKeyCreate, MCPApiKeyUpdate, MCPSettingsResponse, MCPSettingsUpdate
from app.redis_client import redis_client

logger = logging.getLogger("yeyi.mcp")

SETTINGS_CACHE_KEY = "mcp:runtime-settings:v2"
CLEANUP_LOCK_KEY = "mcp:log-cleanup:v1"


@dataclass(frozen=True)
class MCPRuntimeSettings:
    enabled: bool
    rate_limit: int
    rate_window: int
    allowed_hosts: list[str]
    allowed_origins: list[str]
    keys: tuple["MCPRuntimeKey", ...]


@dataclass(frozen=True)
class MCPRuntimeKey:
    id: int | None
    name: str
    api_key: str
    fingerprint: str


def _fernet() -> Fernet:
    if not settings.MCP_SETTINGS_ENCRYPTION_KEY:
        raise RuntimeError("MCP_SETTINGS_ENCRYPTION_KEY must be configured")
    try:
        return Fernet(settings.MCP_SETTINGS_ENCRYPTION_KEY.encode())
    except (ValueError, TypeError) as exc:
        raise RuntimeError("MCP_SETTINGS_ENCRYPTION_KEY is invalid") from exc


def encrypt_api_key(api_key: str) -> str:
    return _fernet().encrypt(api_key.encode()).decode()


def decrypt_api_key(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except (InvalidToken, UnicodeDecodeError) as exc:
        raise RuntimeError("Stored MCP API key cannot be decrypted") from exc


def api_key_fingerprint(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


def _settings_payload(record: MCPServiceSettings, keys: list[MCPApiKey]) -> dict:
    return {
        "enabled": record.enabled,
        "rate_limit": record.rate_limit,
        "rate_window": record.rate_window,
        "allowed_hosts": record.allowed_hosts or [],
        "allowed_origins": record.allowed_origins or [],
        "keys": [
            {
                "id": key.id,
                "name": key.name,
                "api_key_ciphertext": key.api_key_ciphertext,
                "fingerprint": key.fingerprint,
                "enabled": key.enabled,
            }
            for key in keys
        ],
    }


async def get_or_create_settings(db: AsyncSession) -> MCPServiceSettings:
    record = await db.get(MCPServiceSettings, 1)
    if record:
        return record

    api_key = settings.MCP_API_KEY.strip()
    record = MCPServiceSettings(
        id=1,
        enabled=bool(api_key),
        api_key_ciphertext=encrypt_api_key(api_key) if api_key else None,
        api_key_fingerprint=api_key_fingerprint(api_key) if api_key else None,
        api_key_last4=api_key[-4:] if api_key else None,
        rate_limit=settings.MCP_RATE_LIMIT,
        rate_window=settings.MCP_RATE_WINDOW,
        allowed_hosts=settings.MCP_ALLOWED_HOSTS,
        allowed_origins=settings.MCP_ALLOWED_ORIGINS,
        log_retention_days=90,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_or_create_api_keys(db: AsyncSession, record: MCPServiceSettings | None = None) -> list[MCPApiKey]:
    result = await db.execute(select(MCPApiKey).order_by(MCPApiKey.id.asc()))
    keys = list(result.scalars().all())
    if keys:
        return keys

    record = record or await get_or_create_settings(db)
    key = decrypt_api_key(record.api_key_ciphertext) if record.api_key_ciphertext else settings.MCP_API_KEY.strip()
    if not key:
        return []
    bootstrap = MCPApiKey(
        name="default",
        api_key_ciphertext=encrypt_api_key(key),
        fingerprint=api_key_fingerprint(key),
        last4=key[-4:],
        enabled=bool(record.enabled),
    )
    db.add(bootstrap)
    await db.flush()
    return [bootstrap]


def serialize_settings(record: MCPServiceSettings) -> MCPSettingsResponse:
    return MCPSettingsResponse(
        enabled=record.enabled,
        api_key_configured=bool(record.api_key_ciphertext),
        api_key_fingerprint=record.api_key_fingerprint,
        api_key_last4=record.api_key_last4,
        rate_limit=record.rate_limit,
        rate_window=record.rate_window,
        allowed_hosts=record.allowed_hosts or [],
        allowed_origins=record.allowed_origins or [],
        log_retention_days=record.log_retention_days,
        public_url=settings.MCP_PUBLIC_URL,
        updated_at=record.updated_at,
    )


def serialize_api_key(key: MCPApiKey):
    return key


async def invalidate_runtime_settings_cache() -> None:
    try:
        await redis_client.delete(SETTINGS_CACHE_KEY)
    except Exception:
        logger.warning("mcp_settings_cache_invalidation_failed")


async def update_settings(db: AsyncSession, data: MCPSettingsUpdate, admin_user_id: int) -> MCPServiceSettings:
    record = await get_or_create_settings(db)
    keys = await get_or_create_api_keys(db, record)
    updates = data.model_dump(exclude_unset=True)
    api_key = updates.pop("api_key", None)
    if api_key is not None:
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("MCP API key cannot be empty")
        record.api_key_ciphertext = encrypt_api_key(api_key)
        record.api_key_fingerprint = api_key_fingerprint(api_key)
        record.api_key_last4 = api_key[-4:]
        default_key = next((key for key in keys if key.name == "default"), None)
        if default_key is None:
            default_key = MCPApiKey(name="default", api_key_ciphertext="", fingerprint="", last4="", enabled=True)
            db.add(default_key)
            await db.flush()
        default_key.api_key_ciphertext = encrypt_api_key(api_key)
        default_key.fingerprint = api_key_fingerprint(api_key)
        default_key.last4 = api_key[-4:]
        default_key.enabled = True

    for field, value in updates.items():
        setattr(record, field, value)
    if record.enabled and not record.api_key_ciphertext:
        raise ValueError("Configure an MCP API key before enabling the service")

    record.updated_by_id = admin_user_id
    await db.flush()
    await db.refresh(record)
    return record


def _legacy_runtime_settings() -> MCPRuntimeSettings:
    key = settings.MCP_API_KEY or None
    return MCPRuntimeSettings(
        enabled=bool(key),
        rate_limit=settings.MCP_RATE_LIMIT,
        rate_window=settings.MCP_RATE_WINDOW,
        allowed_hosts=settings.MCP_ALLOWED_HOSTS,
        allowed_origins=settings.MCP_ALLOWED_ORIGINS,
        keys=((MCPRuntimeKey(id=None, name="bootstrap", api_key=key, fingerprint=api_key_fingerprint(key)),) if key else ()),
    )


def _runtime_from_payload(payload: dict) -> MCPRuntimeSettings:
    keys = tuple(
        MCPRuntimeKey(
            id=item.get("id"),
            name=item.get("name") or "unnamed",
            api_key=decrypt_api_key(item["api_key_ciphertext"]),
            fingerprint=item["fingerprint"],
        )
        for item in payload.get("keys", [])
        if item.get("enabled") and item.get("api_key_ciphertext")
    )
    return MCPRuntimeSettings(
        enabled=bool(payload.get("enabled")),
        rate_limit=int(payload["rate_limit"]),
        rate_window=int(payload["rate_window"]),
        allowed_hosts=list(payload.get("allowed_hosts") or []),
        allowed_origins=list(payload.get("allowed_origins") or []),
        keys=keys,
    )


async def get_runtime_settings() -> MCPRuntimeSettings:
    # Keeps local MCP protocol tests and pre-migration deployments compatible.
    if not settings.MCP_SETTINGS_ENCRYPTION_KEY:
        return _legacy_runtime_settings()
    try:
        cached = await redis_client.get(SETTINGS_CACHE_KEY)
        if cached:
            return _runtime_from_payload(json.loads(cached))
    except Exception:
        logger.warning("mcp_settings_cache_unavailable")

    try:
        async with async_session() as db:
            record = await get_or_create_settings(db)
            keys = await get_or_create_api_keys(db, record)
            payload = _settings_payload(record, keys)
            await db.commit()
        try:
            await redis_client.set(SETTINGS_CACHE_KEY, json.dumps(payload), ex=300)
        except Exception:
            logger.warning("mcp_settings_cache_write_failed")
        return _runtime_from_payload(payload)
    except Exception:
        logger.exception("mcp_settings_database_unavailable")
        return _legacy_runtime_settings()


async def record_request_log(
    *,
    request_id: str,
    client_ip: str | None,
    user_agent: str | None,
    rpc_method: str | None,
    tool_name: str | None,
    success: bool,
    http_status: int | None,
    duration_ms: int | None = None,
    error_message: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    resource_slug: str | None = None,
    key_id: int | None = None,
    key_name: str | None = None,
    key_fingerprint: str | None = None,
) -> None:
    async with async_session() as db:
        db.add(MCPRequestLog(
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
            rpc_method=rpc_method,
            tool_name=tool_name,
            success=success,
            http_status=http_status,
            duration_ms=duration_ms,
            error_message=error_message[:500] if error_message else None,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_slug=resource_slug,
            api_key_id=key_id,
            api_key_name=key_name,
            api_key_fingerprint=key_fingerprint,
        ))
        await db.commit()
    await maybe_cleanup_expired_logs()


async def list_request_logs(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
    tool_name: str | None = None,
    success: bool | None = None,
    client_ip: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    api_key_id: int | None = None,
) -> tuple[list[MCPRequestLog], int]:
    query = select(MCPRequestLog)
    if tool_name:
        query = query.where(MCPRequestLog.tool_name == tool_name)
    if success is not None:
        query = query.where(MCPRequestLog.success == success)
    if client_ip:
        query = query.where(MCPRequestLog.client_ip == client_ip)
    if api_key_id:
        query = query.where(MCPRequestLog.api_key_id == api_key_id)
    if start_at:
        query = query.where(MCPRequestLog.created_at >= start_at)
    if end_at:
        query = query.where(MCPRequestLog.created_at <= end_at)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.order_by(MCPRequestLog.created_at.desc(), MCPRequestLog.id.desc()).offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def list_api_keys(db: AsyncSession) -> list[MCPApiKey]:
    return list((await db.execute(select(MCPApiKey).order_by(MCPApiKey.created_at.desc(), MCPApiKey.id.desc()))).scalars().all())


async def create_api_key(db: AsyncSession, data: MCPApiKeyCreate, admin_user_id: int) -> MCPApiKey:
    key = data.api_key.strip()
    fingerprint = api_key_fingerprint(key)
    existing = await db.execute(select(MCPApiKey).where(MCPApiKey.fingerprint == fingerprint))
    if existing.scalar_one_or_none():
        raise ValueError("An MCP API key with the same value already exists")
    record = MCPApiKey(
        name=data.name.strip(),
        api_key_ciphertext=encrypt_api_key(key),
        fingerprint=fingerprint,
        last4=key[-4:],
        enabled=True,
        created_by_id=admin_user_id,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def update_api_key(db: AsyncSession, key_id: int, data: MCPApiKeyUpdate) -> MCPApiKey:
    record = await db.get(MCPApiKey, key_id)
    if not record:
        raise ValueError("MCP API key not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


async def delete_api_key(db: AsyncSession, key_id: int) -> None:
    record = await db.get(MCPApiKey, key_id)
    if not record:
        raise ValueError("MCP API key not found")
    await db.delete(record)
    await db.flush()


async def export_api_key_url(db: AsyncSession, key_id: int) -> str:
    record = await db.get(MCPApiKey, key_id)
    if not record:
        raise ValueError("MCP API key not found")
    key = decrypt_api_key(record.api_key_ciphertext)
    parsed = urlsplit(settings.MCP_PUBLIC_URL)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["tavilyApiKey"] = key
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), urlencode(query), parsed.fragment))


async def record_api_key_usage(key_id: int | None) -> None:
    if key_id is None:
        return
    async with async_session() as db:
        await db.execute(update(MCPApiKey).where(MCPApiKey.id == key_id).values(
            usage_count=MCPApiKey.usage_count + 1,
            last_used_at=func.now(),
        ))
        await db.commit()


async def get_overview(db: AsyncSession) -> tuple[MCPServiceSettings, int, int, int]:
    record = await get_or_create_settings(db)
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    total = (await db.execute(select(func.count()).select_from(MCPRequestLog).where(MCPRequestLog.created_at >= since))).scalar() or 0
    successful = (await db.execute(select(func.count()).select_from(MCPRequestLog).where(MCPRequestLog.created_at >= since, MCPRequestLog.success.is_(True)))).scalar() or 0
    return record, total, successful, total - successful


async def cleanup_expired_logs(db: AsyncSession) -> int:
    record = await get_or_create_settings(db)
    before = datetime.now(timezone.utc) - timedelta(days=record.log_retention_days)
    result = await db.execute(delete(MCPRequestLog).where(MCPRequestLog.created_at < before))
    return int(result.rowcount or 0)


async def maybe_cleanup_expired_logs() -> None:
    try:
        acquired = await redis_client.set(CLEANUP_LOCK_KEY, "1", ex=3600, nx=True)
        if not acquired:
            return
        async with async_session() as db:
            await cleanup_expired_logs(db)
            await db.commit()
    except Exception:
        logger.warning("mcp_log_cleanup_failed")
