from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.mcp.server import delete_post, mcp, mcp_http_app, upload_image


def mock_redis():
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.eval = AsyncMock(return_value=1)
    pipe = MagicMock()
    pipe.incr = MagicMock()
    pipe.expire = MagicMock()
    pipe.execute = AsyncMock(return_value=[1, 1])
    redis.pipeline.return_value = pipe
    return redis


@pytest.fixture
def mcp_settings():
    old_key = settings.MCP_API_KEY
    old_required = settings.MCP_REQUIRE_API_KEY
    settings.MCP_API_KEY = "test-mcp-key"
    settings.MCP_REQUIRE_API_KEY = True
    yield
    settings.MCP_API_KEY = old_key
    settings.MCP_REQUIRE_API_KEY = old_required


async def request(client: httpx.AsyncClient, headers: dict[str, str], payload: dict):
    return await client.post(
        "/mcp",
        headers={
            **headers,
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
        },
        json=payload,
    )


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_mcp_auth_and_initialize(mcp_settings):
    transport = httpx.ASGITransport(app=mcp_http_app)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1"},
        },
    }
    redis = mock_redis()
    with patch("app.mcp.auth.redis_client", redis):
        async with mcp_http_app.router.lifespan_context(mcp_http_app):
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                assert (await request(client, {}, payload)).status_code == 401
                assert (await request(client, {"X-MCP-API-Key": "wrong"}, payload)).status_code == 401
                query_response = await client.post(
                    "/mcp?tavilyApiKey=test-mcp-key",
                    headers={"content-type": "application/json", "accept": "application/json, text/event-stream"},
                    json=payload,
                )
                assert query_response.status_code == 200
                response = await request(client, {"X-MCP-API-Key": "test-mcp-key"}, payload)

    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "yeyi_blog_mcp"
    redis.eval.assert_awaited()


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_mcp_health_is_public(mcp_settings):
    transport = httpx.ASGITransport(app=mcp_http_app)
    with patch("app.mcp.auth.redis_client", mock_redis()):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_mcp_exposes_management_tools():
    names = {tool.name for tool in await mcp.list_tools()}
    assert {"yeyi_blog_create_post", "yeyi_blog_update_post", "yeyi_blog_publish_post", "yeyi_blog_create_comment", "yeyi_blog_update_site_config", "yeyi_blog_upload_image"} <= names

    tools = {tool.name: tool for tool in await mcp.list_tools()}
    assert tools["yeyi_blog_list_posts"].annotations.readOnlyHint is True
    assert tools["yeyi_blog_delete_post"].annotations.destructiveHint is True
    assert tools["yeyi_blog_list_posts"].outputSchema["properties"]["has_more"]["type"] == "boolean"
    assert all(tool.annotations is not None and tool.outputSchema for tool in tools.values())
    assert tools["yeyi_blog_upload_image"].inputSchema["properties"]["content_base64"]["type"] == "string"


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_delete_requires_confirmation():
    with pytest.raises(ValueError, match="confirm=true"):
        await delete_post(1)


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_rejects_traversal_and_oversized_base64(mcp_settings):
    with pytest.raises(ValueError, match="simple file name"):
        await upload_image("..\\secret.png", "aA==")
    with pytest.raises(ValueError, match="upload limit"):
        with patch("app.mcp.server.settings.MAX_UPLOAD_SIZE", 3):
            await upload_image("ok.png", "QUJDRA==")
    with pytest.raises(ValueError, match="invalid"):
        await upload_image("ok.png", "not-base64!")


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_mcp_host_allowlist(mcp_settings):
    old_hosts = settings.MCP_ALLOWED_HOSTS
    settings.MCP_ALLOWED_HOSTS = ["allowed.example"]
    payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "pytest", "version": "1"}}}
    try:
        with patch("app.mcp.auth.redis_client", mock_redis()):
            transport = httpx.ASGITransport(app=mcp_http_app)
            async with httpx.AsyncClient(transport=transport, base_url="http://wrong.example") as client:
                response = await request(client, {"X-MCP-API-Key": "test-mcp-key"}, payload)
        assert response.status_code == 403
    finally:
        settings.MCP_ALLOWED_HOSTS = old_hosts
