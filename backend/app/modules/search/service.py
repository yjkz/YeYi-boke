from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.posts.model import Post


async def search_posts(db: AsyncSession, query: str, offset: int = 0, limit: int = 10) -> tuple[list[Post], int]:
    search_term = f"%{query}%"
    base = (
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags))
        .where(Post.status == "published")
        .where(
            Post.title.like(search_term)
            | Post.content_md.like(search_term)
            | Post.excerpt.like(search_term)
        )
        .order_by(Post.published_at.desc())
    )

    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(base.offset(offset).limit(limit))
    return list(result.scalars().unique().all()), total
