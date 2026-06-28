from feedgen.feed import FeedGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.modules.config.service import get_all_config
from app.modules.posts.model import Post


async def generate_rss(db: AsyncSession) -> str:
    config = await get_all_config(db)
    site_url = settings.SITE_URL
    fg = FeedGenerator()
    fg.title(config.get("site_title", "YeYi Blog"))
    fg.link(href=site_url)
    fg.description(config.get("site_subtitle", ""))

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.category))
        .where(Post.status == "published")
        .order_by(Post.published_at.desc())
        .limit(20)
    )
    posts = result.scalars().all()

    for post in posts:
        fe = fg.add_entry()
        fe.title(post.title)
        fe.link(href=f"{site_url}/posts/{post.slug}")
        fe.description(post.excerpt or "")
        if post.published_at:
            fe.pubDate(post.published_at.replace(tzinfo=None))

    return fg.rss_str(pretty=True).decode("utf-8")
