from pydantic import BaseModel


class VisitRequest(BaseModel):
    page_path: str
    page_title: str | None = None


class StatsOverview(BaseModel):
    today_pv: int
    total_posts: int
    total_comments: int


class PublicStatsSummary(BaseModel):
    today_pv: int
    published_posts: int
    categories: int
    tags: int
    approved_comments: int


class TrendPoint(BaseModel):
    date: str
    page_views: int
    unique_visitors: int


class StatsTrendResponse(BaseModel):
    data: list[TrendPoint]
