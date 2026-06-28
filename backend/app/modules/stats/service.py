from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comments.model import Comment
from app.modules.posts.model import Post
from app.modules.stats.model import VisitLog, VisitStats


async def record_visit(db: AsyncSession, page_path: str, page_title: str | None, visitor_ip: str | None, user_agent: str | None, referer: str | None) -> None:
    log = VisitLog(
        page_path=page_path,
        page_title=page_title,
        visitor_ip=visitor_ip,
        user_agent=user_agent,
        referer=referer,
    )
    db.add(log)


async def get_stats_overview(db: AsyncSession) -> dict:
    today = date.today()
    today_pv = (await db.execute(
        select(func.count()).where(func.date(VisitLog.created_at) == today)
    )).scalar() or 0

    total_posts = (await db.execute(
        select(func.count()).where(Post.status == "published")
    )).scalar() or 0

    total_comments = (await db.execute(
        select(func.count()).where(Comment.status == "approved")
    )).scalar() or 0

    return {"today_pv": today_pv, "total_posts": total_posts, "total_comments": total_comments}


async def get_stats_trend(db: AsyncSession, days: int = 7) -> list[dict]:
    start_date = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(VisitLog.created_at).label("stat_date"),
            func.count().label("page_views"),
            func.count(func.distinct(VisitLog.visitor_ip)).label("unique_visitors"),
        )
        .where(func.date(VisitLog.created_at) >= start_date)
        .group_by(func.date(VisitLog.created_at))
        .order_by(func.date(VisitLog.created_at))
    )
    return [
        {"date": str(row.stat_date), "page_views": row.page_views, "unique_visitors": row.unique_visitors}
        for row in result.all()
    ]
