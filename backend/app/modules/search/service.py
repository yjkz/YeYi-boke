from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.posts.model import Post
from app.utils.markdown import excerpt_from_markdown


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
    posts = list(result.scalars().unique().all())
    for post in posts:
        if post.excerpt:
            source = post.content_md if post.content_md and post.excerpt == post.content_md[:200] else post.excerpt
            post.excerpt = excerpt_from_markdown(source)
    return posts, total
