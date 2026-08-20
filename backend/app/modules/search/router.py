from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination
from app.modules.search import service as search_service
from app.modules.posts.schema import PostListResponse
from app.middleware.rate_limit import rate_limit

router = APIRouter(tags=["search"])


@router.get("/search", response_model=PostListResponse, dependencies=[Depends(rate_limit(30, 60))])
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    posts, total = await search_service.search_posts(db, q, offset=pagination.offset, limit=pagination.page_size)
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}
