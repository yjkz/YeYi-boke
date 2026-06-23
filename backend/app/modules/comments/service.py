from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.comments.model import Comment
from app.modules.posts.model import Post


async def create_comment(db: AsyncSession, post_slug: str, nickname: str, content: str, email: str | None = None, website: str | None = None, parent_id: int | None = None, visitor_ip: str | None = None) -> Comment | None:
    result = await db.execute(select(Post.id).where(Post.slug == post_slug))
    post_id = result.scalar_one_or_none()
    if not post_id:
        return None

    comment = Comment(
        post_id=post_id,
        parent_id=parent_id,
        nickname=nickname,
        email=email,
        website=website,
        content=content,
        visitor_ip=visitor_ip,
    )
    db.add(comment)
    await db.flush()
    return comment


async def get_approved_comments(db: AsyncSession, post_slug: str) -> list[Comment]:
    result = await db.execute(
        select(Post.id).where(Post.slug == post_slug)
    )
    post_id = result.scalar_one_or_none()
    if not post_id:
        return []

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.status == "approved", Comment.parent_id.is_(None))
        .order_by(Comment.created_at)
    )
    return list(result.scalars().all())


async def get_admin_comments(db: AsyncSession, offset: int = 0, limit: int = 20, status: str | None = None):
    query = select(Comment)
    if status:
        query = query.where(Comment.status == status)
    query = query.order_by(Comment.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def update_comment_status(db: AsyncSession, comment_id: int, status: str) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        return None
    comment.status = status
    await db.flush()
    return comment


async def delete_comment(db: AsyncSession, comment_id: int) -> bool:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        return False
    await db.delete(comment)
    await db.flush()
    return True
