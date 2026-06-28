from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, get_current_user
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
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await post_service.increment_view_count(db, post)
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
    _user: User = Depends(get_current_user),
):
    posts, total = await post_service.get_posts(db, offset=pagination.offset, limit=pagination.page_size, status=post_status)
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.post("/admin/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_post(db, data)


@router.put("/admin/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, data: PostUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.update_post(db, post_id, data)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/admin/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not await post_service.delete_post(db, post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/admin/posts/{post_id}/publish", response_model=PostResponse)
async def publish_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.publish_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/posts/{post_id}/draft", response_model=PostResponse)
async def draft_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.draft_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_category(db, data.name, data.slug, data.description, data.sort_order)


@router.post("/admin/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_tag(db, data.name, data.slug)
