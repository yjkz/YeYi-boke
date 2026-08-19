from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, get_current_user, require_admin
from app.modules.config.service import get_all_config
from app.modules.comments import service as comment_service
from app.modules.comments.schema import AdminCommentListResponse, CommentCreate, CommentCreateResponse, CommentResponse, CommentUpdate
from app.modules.users.model import User

router = APIRouter(tags=["comments"])


@router.post("/comments", response_model=CommentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentCreate, request: Request, db: AsyncSession = Depends(get_db)):
    config = await get_all_config(db)
    if not config.get("comment_enabled", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comments are disabled")
    comment_status = "pending" if config.get("comment_need_review", True) else "approved"
    comment = await comment_service.create_comment(
        db, post_slug=body.post_slug, nickname=body.nickname, content=body.content,
        email=body.email, website=body.website, parent_id=body.parent_id,
        visitor_ip=request.client.host if request.client else None,
        status=comment_status,
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return comment


@router.get("/posts/{slug}/comments", response_model=list[CommentResponse])
async def get_comments(slug: str, db: AsyncSession = Depends(get_db)):
    return await comment_service.get_approved_comments(db, slug)


@router.get("/admin/comments", response_model=AdminCommentListResponse)
async def admin_list_comments(
    pagination: Pagination = Depends(),
    comment_status: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    items, total = await comment_service.get_admin_comments(db, offset=pagination.offset, limit=pagination.page_size, status=comment_status)
    return {"items": items, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.put("/admin/comments/{comment_id}", response_model=CommentCreateResponse)
async def update_comment(comment_id: int, body: CommentUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    comment = await comment_service.update_comment_status(db, comment_id, body.status)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/admin/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    if not await comment_service.delete_comment(db, comment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
