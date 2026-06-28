from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.redis_client import redis_client
from app.dependencies import Pagination, get_current_user, require_admin
from app.modules.users.model import User
from app.modules.posts import service as post_service
from app.modules.posts.rss import generate_rss
from app.modules.posts.schema import (
    CategoryCreate, CategoryResponse, PostCreate, PostListResponse,
    PostResponse, PostUpdate, TagCreate, TagResponse,
)

router = APIRouter(tags=["posts"])


# -- Public --

@router.get("/posts", response_model=PostListResponse)
async def list_posts(
    pagination: Pagination = Depends(),
    category: str | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    posts, total = await post_service.get_posts(db, offset=pagination.offset, limit=pagination.page_size, category_slug=category, tag_slug=tag, status="published")
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_post(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    ip = request.client.host if request.client else "unknown"
    viewed = await redis_client.get(f"view:{ip}:{slug}")
    if not viewed:
        await post_service.increment_view_count(db, post)
        await redis_client.set(f"view:{ip}:{slug}", "1", ex=3600)
    return post


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await post_service.get_categories(db)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await post_service.get_tags(db)


@router.get("/rss.xml")
async def rss(db: AsyncSession = Depends(get_db)):
    xml = await generate_rss(db)
    return Response(content=xml, media_type="application/rss+xml")


# -- Admin --

@router.get("/admin/posts", response_model=PostListResponse)
async def admin_list_posts(
    pagination: Pagination = Depends(),
    post_status: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    posts, total = await post_service.get_posts(db, offset=pagination.offset, limit=pagination.page_size, status=post_status)
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.get("/admin/posts/{post_id}", response_model=PostResponse)
async def admin_get_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    post = await post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        return await post_service.create_post(db, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")


@router.put("/admin/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, data: PostUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        post = await post_service.update_post(db, post_id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/admin/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    if not await post_service.delete_post(db, post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/admin/posts/{post_id}/publish", response_model=PostResponse)
async def publish_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    post = await post_service.publish_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/posts/{post_id}/draft", response_model=PostResponse)
async def draft_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    post = await post_service.draft_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        return await post_service.create_category(db, data.name, data.slug, data.description, data.sort_order)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category slug already exists")


@router.put("/admin/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, data: CategoryCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        category = await post_service.update_category(db, category_id, data.name, data.slug, data.description, data.sort_order)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category slug already exists")
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    if not await post_service.delete_category(db, category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@router.post("/admin/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        return await post_service.create_tag(db, data.name, data.slug)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag slug already exists")


@router.put("/admin/tags/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, data: TagCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    try:
        tag = await post_service.update_tag(db, tag_id, data.name, data.slug)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag slug already exists")
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/admin/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    if not await post_service.delete_tag(db, tag_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
