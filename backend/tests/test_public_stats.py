import pytest
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_public_stats_summary_is_public_and_has_stable_fields(client: AsyncClient):
    response = await client.get("/api/v1/stats/summary")

    assert response.status_code == 200
    assert response.json() == {
        "today_pv": 0,
        "published_posts": 0,
        "categories": 0,
        "tags": 0,
        "approved_comments": 0,
    }


@pytest.mark.asyncio
async def test_avatar_url_has_empty_default_and_can_be_updated(client: AsyncClient, auth_headers):
    public_response = await client.get("/api/v1/site/config")
    assert public_response.status_code == 200
    assert public_response.json()["avatar_url"] == ""

    update_response = await client.put(
        "/api/v1/admin/site/config",
        headers=auth_headers,
        json={"avatar_url": "/uploads/avatar.png"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["avatar_url"] == "/uploads/avatar.png"
