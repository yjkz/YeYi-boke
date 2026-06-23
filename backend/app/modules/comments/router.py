from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, get_current_user
from app.modules.comments import service as comment_service
from app.modules.comments.schema import AdminCommentListResponse, CommentCreate, CommentResponse, CommentUpdate
from app.modules.users.model import User

router = APIRouter(tags=["comments"])


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentCreate, request: Request, db: AsyncSession = Depends(get_db)):
    comment = await comment_service.create_comment(
        db, post_slug=body.post_slug, nickname=body.nickname, content=body.content,
        email=body.email, website=body.website, parent_id=body.parent_id,
        visitor_ip=request.client.host if request.client else None,
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
    _user: User = Depends(get_current_user),
):
    items, total = await comment_service.get_admin_comments(db, offset=pagination.offset, limit=pagination.page_size, status=comment_status)
    return {"items": items, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.put("/admin/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, body: CommentUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    comment = await comment_service.update_comment_status(db, comment_id, body.status)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/admin/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not await comment_service.delete_comment(db, comment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
