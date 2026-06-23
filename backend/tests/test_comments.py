import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, auth_headers):
    # Create and publish a post first
    create_resp = await client.post(
        "/api/v1/admin/posts",
        json={"title": "C", "slug": "c", "content_md": "x"},
        headers=auth_headers,
    )
    post_id = create_resp.json()["id"]
    await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)

    resp = await client.post("/api/v1/comments", json={
        "post_slug": "c",
        "nickname": "visitor",
        "content": "nice post!",
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_admin_approve_comment(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/admin/posts",
        json={"title": "C2", "slug": "c2", "content_md": "x"},
        headers=auth_headers,
    )
    post_id = create_resp.json()["id"]
    await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)

    comment_resp = await client.post(
        "/api/v1/comments",
        json={"post_slug": "c2", "nickname": "v", "content": "hello"},
    )
    comment_id = comment_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/admin/comments/{comment_id}",
        json={"status": "approved"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
