import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong1"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_refresh_rotates_refresh_token(client: AsyncClient, admin_user):
    class RefreshRedis:
        def __init__(self):
            self.values = {}

        async def set(self, key, value, **kwargs):
            self.values[key] = value

        async def get(self, key):
            return self.values.get(key)

        async def delete(self, key):
            self.values.pop(key, None)

    from app.modules.users import service as user_service
    from unittest.mock import patch

    with patch.object(user_service, "redis_client", RefreshRedis()):
        login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        old_refresh = login.json()["refresh_token"]

        refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        reused = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != old_refresh
    assert reused.status_code == 401
