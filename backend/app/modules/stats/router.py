from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.modules.stats import service as stats_service
from app.modules.stats.schema import PublicStatsSummary, StatsOverview, StatsTrendResponse, VisitRequest
from app.modules.users.model import User

router = APIRouter(tags=["stats"])


@router.post("/visit", status_code=204)
async def record_visit(body: VisitRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await stats_service.record_visit(
        db,
        page_path=body.page_path,
        page_title=body.page_title,
        visitor_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
    )


@router.get("/stats/summary", response_model=PublicStatsSummary)
async def get_public_summary(db: AsyncSession = Depends(get_db)):
    return await stats_service.get_public_stats_summary(db)


@router.get("/admin/stats", response_model=StatsOverview)
async def get_overview(db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    return await stats_service.get_stats_overview(db)


@router.get("/admin/stats/trend", response_model=StatsTrendResponse)
async def get_trend(days: int = Query(7, ge=1, le=90), db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    data = await stats_service.get_stats_trend(db, days)
    return {"data": data}
