from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.modules.config import service as config_service
from app.modules.config.schema import AnnouncementResponse, SiteConfigResponse, SiteConfigUpdate
from app.modules.users.model import User

router = APIRouter(tags=["site"])


@router.get("/site/config", response_model=SiteConfigResponse)
async def get_site_config(db: AsyncSession = Depends(get_db)):
    return await config_service.get_all_config(db)


@router.get("/site/announcement", response_model=AnnouncementResponse)
async def get_announcement(db: AsyncSession = Depends(get_db)):
    content = await config_service.get_announcement(db)
    return {"content": content}


@router.put("/admin/site/config", response_model=SiteConfigResponse)
async def update_site_config(body: SiteConfigUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    updates = body.model_dump(exclude_unset=True)
    await config_service.update_config(db, updates)
    return await config_service.get_all_config(db)
