from app.config import settings

if settings.MCP_REQUIRE_API_KEY and not settings.MCP_SETTINGS_ENCRYPTION_KEY:
    raise RuntimeError("MCP_SETTINGS_ENCRYPTION_KEY must be configured before starting the MCP server")

from app.mcp.server import mcp_http_app as app

__all__ = ["app"]
