from datetime import datetime, timedelta

import pytest
from cryptography.fernet import Fernet
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.mcp.model import MCPRequestLog, MCPServiceSettings


@pytest.fixture
def mcp_runtime_config(monkeypatch):
    monkeypatch.setattr(settings, "MCP_SETTINGS_ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.setattr(settings, "MCP_API_KEY", "bootstrap-mcp-key")
    monkeypatch.setattr(settings, "MCP_PUBLIC_URL", "https://mcp.test/mcp")


@pytest.mark.asyncio
async def test_admin_can_update_mcp_settings_without_exposing_key(
    client: AsyncClient,
    auth_headers: dict,
    db: AsyncSession,
    mcp_runtime_config,
):
    response = await client.put("/api/v1/admin/mcp/settings", headers=auth_headers, json={
        "enabled": True,
        "api_key": "rotated-mcp-key",
        "rate_limit": 42,
        "rate_window": 30,
        "allowed_hosts": ["mcp.test"],
        "allowed_origins": ["https://mcp.test"],
        "log_retention_days": 30,
    })

    assert response.status_code == 200
    payload = response.json()
    assert "api_key" not in payload
    assert payload["api_key_configured"] is True
    assert payload["api_key_last4"] == "-key"
    assert payload["rate_limit"] == 42

    # The admin fixture refreshed its user in an earlier MySQL transaction.
    # End that repeatable-read snapshot before verifying the request's commit.
    await db.rollback()
    record = (await db.execute(select(MCPServiceSettings))).scalar_one()
    assert record.api_key_ciphertext != "rotated-mcp-key"
    assert "rotated-mcp-key" not in record.api_key_ciphertext


@pytest.mark.asyncio
async def test_mcp_log_list_detail_and_cleanup(
    client: AsyncClient,
    auth_headers: dict,
    db: AsyncSession,
    mcp_runtime_config,
):
    old = MCPRequestLog(
        request_id="old-request", client_ip="203.0.113.5", user_agent="pytest",
        rpc_method="tools/call", tool_name="yeyi_blog_update_post", success=False,
        http_status=200, duration_ms=12, error_message="Post not found", resource_type="post",
        resource_id="99", resource_slug="old-post", api_key_fingerprint="abc", created_at=datetime.utcnow() - timedelta(days=2),
    )
    current = MCPRequestLog(
        request_id="current-request", client_ip="203.0.113.5", user_agent="pytest",
        rpc_method="tools/call", tool_name="yeyi_blog_list_posts", success=True,
        http_status=200, duration_ms=4, resource_type=None, resource_id=None, resource_slug=None,
        api_key_fingerprint="abc", created_at=datetime.utcnow(),
    )
    db.add_all([old, current])
    await db.commit()
    await db.refresh(current)

    response = await client.get("/api/v1/admin/mcp/logs", headers=auth_headers, params={"tool_name": "yeyi_blog_list_posts", "success": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["client_ip"] == "203.0.113.5"
    assert payload["items"][0]["tool_name"] == "yeyi_blog_list_posts"

    detail = await client.get(f"/api/v1/admin/mcp/logs/{current.id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["request_id"] == "current-request"

    await client.put("/api/v1/admin/mcp/settings", headers=auth_headers, json={"log_retention_days": 1})
    cleanup = await client.post("/api/v1/admin/mcp/logs/cleanup", headers=auth_headers)
    assert cleanup.status_code == 200
    assert cleanup.json()["deleted_count"] == 1


@pytest.mark.asyncio
async def test_admin_can_manage_multiple_mcp_api_keys(client: AsyncClient, auth_headers: dict, db: AsyncSession, mcp_runtime_config):
    created = await client.post(
        "/api/v1/admin/mcp/keys",
        headers=auth_headers,
        json={"name": "Tavily connector", "api_key": "tavily-local-key"},
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["name"] == "Tavily connector"
    assert payload["last4"] == "-key"
    assert "api_key" not in payload
    key_id = payload["id"]

    exported = await client.get(f"/api/v1/admin/mcp/keys/{key_id}/export-url", headers=auth_headers)
    assert exported.status_code == 200
    assert exported.json()["url"] == "https://mcp.test/mcp?tavilyApiKey=tavily-local-key"

    listed = await client.get("/api/v1/admin/mcp/keys", headers=auth_headers)
    assert listed.status_code == 200
    assert any(item["id"] == key_id and item["usage_count"] == 0 for item in listed.json()["items"])

    disabled = await client.patch(f"/api/v1/admin/mcp/keys/{key_id}", headers=auth_headers, json={"enabled": False})
    assert disabled.status_code == 200
    assert disabled.json()["enabled"] is False

    deleted = await client.delete(f"/api/v1/admin/mcp/keys/{key_id}", headers=auth_headers)
    assert deleted.status_code == 204
