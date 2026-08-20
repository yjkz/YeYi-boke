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


@pytest.mark.asyncio
async def test_comment_reply_must_belong_to_same_post(client: AsyncClient, auth_headers):
    first = await client.post(
        "/api/v1/admin/posts",
        json={"title": "First", "slug": "first", "content_md": "x"},
        headers=auth_headers,
    )
    second = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Second", "slug": "second", "content_md": "x"},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/admin/posts/{first.json()['id']}/publish", headers=auth_headers)
    await client.post(f"/api/v1/admin/posts/{second.json()['id']}/publish", headers=auth_headers)

    parent = await client.post(
        "/api/v1/comments",
        json={"post_slug": "first", "nickname": "v", "content": "parent"},
    )
    reply = await client.post(
        "/api/v1/comments",
        json={"post_slug": "second", "parent_id": parent.json()["id"], "nickname": "v2", "content": "reply"},
    )

    assert reply.status_code == 400


@pytest.mark.asyncio
async def test_admin_comments_include_post_context_and_filter(client: AsyncClient, auth_headers):
    post = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Context Post", "slug": "context-post", "content_md": "x"},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/admin/posts/{post.json()['id']}/publish", headers=auth_headers)
    await client.post(
        "/api/v1/comments",
        json={"post_slug": "context-post", "nickname": "v", "content": "hello"},
    )

    result = await client.get(
        "/api/v1/admin/comments",
        params={"post_title": "Context"},
        headers=auth_headers,
    )

    assert result.json()["total"] == 1
    assert result.json()["items"][0]["post_title"] == "Context Post"
    assert result.json()["items"][0]["post_slug"] == "context-post"
