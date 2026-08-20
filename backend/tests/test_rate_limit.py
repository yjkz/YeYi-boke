import pytest
from httpx import AsyncClient


class FakeRateRedis:
    def __init__(self):
        self.counts = {}

    async def get(self, key):
        return self.counts.get(key)

    def pipeline(self):
        return self

    def incr(self, key):
        self._key = key
        return self

    def expire(self, key, window):
        return self

    async def execute(self):
        self.counts[self._key] = self.counts.get(self._key, 0) + 1
        return [self.counts[self._key], True]


@pytest.mark.asyncio
async def test_login_is_rate_limited(client: AsyncClient, admin_user, monkeypatch):
    fake = FakeRateRedis()
    monkeypatch.setattr("app.middleware.rate_limit.redis_client", fake)

    responses = [
        await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong1"})
        for _ in range(11)
    ]

    assert responses[-1].status_code == 429
