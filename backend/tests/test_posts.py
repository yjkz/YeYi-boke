import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers):
    resp = await client.post("/api/v1/admin/posts", json={
        "title": "Test Post",
        "slug": "test-post",
        "content_md": "# Hello\n\nThis is a test.",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Post"
    assert "<h1>" in data["content_html"]


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, auth_headers):
    await client.post(
        "/api/v1/admin/posts",
        json={"title": "Post 1", "slug": "post-1", "content_md": "content"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/posts")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0  # draft, not published


@pytest.mark.asyncio
async def test_publish_post(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Pub", "slug": "pub", "content_md": "hi"},
        headers=auth_headers,
    )
    post_id = create_resp.json()["id"]
    resp = await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"

    list_resp = await client.get("/api/v1/posts")
    assert list_resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_public_posts_filter_by_category_and_tag(client: AsyncClient, auth_headers):
    category = await client.post(
        "/api/v1/admin/categories",
        json={"name": "Tech", "slug": "tech"},
        headers=auth_headers,
    )
    tag = await client.post(
        "/api/v1/admin/tags",
        json={"name": "Python", "slug": "python"},
        headers=auth_headers,
    )
    post = await client.post(
        "/api/v1/admin/posts",
        json={
            "title": "Filtered",
            "slug": "filtered",
            "content_md": "content",
            "category_id": category.json()["id"],
            "tag_ids": [tag.json()["id"]],
        },
        headers=auth_headers,
    )
    await client.post(f"/api/v1/admin/posts/{post.json()['id']}/publish", headers=auth_headers)

    category_result = await client.get("/api/v1/posts", params={"category": "tech"})
    tag_result = await client.get("/api/v1/posts", params={"tag": "python"})

    assert category_result.json()["total"] == 1
    assert tag_result.json()["total"] == 1


@pytest.mark.asyncio
async def test_public_posts_latest_sort_ignores_pin_priority(client: AsyncClient, auth_headers):
    older = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Older", "slug": "older", "content_md": "content", "is_top": True},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/admin/posts/{older.json()['id']}/publish", headers=auth_headers)

    newer = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Newer", "slug": "newer", "content_md": "content"},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/admin/posts/{newer.json()['id']}/publish", headers=auth_headers)

    result = await client.get("/api/v1/posts", params={"sort": "latest"})

    assert result.status_code == 200
    assert result.json()["items"][0]["slug"] == "newer"


@pytest.mark.asyncio
async def test_admin_posts_can_filter_by_status(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/admin/posts",
        json={"title": "Draft only", "slug": "draft-only", "content_md": "content"},
        headers=auth_headers,
    )

    result = await client.get("/api/v1/admin/posts", params={"status": "draft"}, headers=auth_headers)

    assert result.json()["total"] == 1
    assert result.json()["items"][0]["id"] == response.json()["id"]


@pytest.mark.asyncio
async def test_rss_returns_published_posts(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/admin/posts",
        json={"title": "RSS Post", "slug": "rss-post", "content_md": "RSS content"},
        headers=auth_headers,
    )
    await client.post(
        f"/api/v1/admin/posts/{create_resp.json()['id']}/publish",
        headers=auth_headers,
    )

    response = await client.get("/api/v1/rss.xml")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/rss+xml")
    assert "RSS Post" in response.text
    assert "http://localhost:3000/posts/rss-post" in response.text
