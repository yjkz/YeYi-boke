import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.model import SiteConfig


DEFAULT_CONFIG = {
    "site_title": "YeYi 的博客",
    "site_subtitle": "记录生活与代码",
    "logo_url": "",
    "favicon_url": "",
    "announcement": "",
    "about_content": "这是 YeYi 的个人博客，记录生活与代码。\n\n使用 Nuxt 3 + FastAPI 构建，采用洛克魔法书设计风格。",
    "footer_text": "© 2026 YeYi",
    "social_links": "{}",
    "comment_enabled": "true",
    "comment_need_review": "true",
}


async def get_all_config(db: AsyncSession) -> dict:
    result = await db.execute(select(SiteConfig))
    rows = result.scalars().all()
    config = {row.config_key: row.config_value for row in rows}
    merged = {**DEFAULT_CONFIG, **config}

    merged["comment_enabled"] = str(merged["comment_enabled"] or "").lower() == "true"
    merged["comment_need_review"] = str(merged["comment_need_review"] or "").lower() == "true"
    try:
        merged["social_links"] = json.loads(merged["social_links"])
    except (json.JSONDecodeError, TypeError):
        merged["social_links"] = {}

    return merged


async def get_announcement(db: AsyncSession) -> str:
    result = await db.execute(select(SiteConfig).where(SiteConfig.config_key == "announcement"))
    row = result.scalar_one_or_none()
    return row.config_value if row else ""


async def update_config(db: AsyncSession, updates: dict) -> None:
    for key, value in updates.items():
        if value is None:
            continue
        result = await db.execute(select(SiteConfig).where(SiteConfig.config_key == key))
        row = result.scalar_one_or_none()
        str_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value).lower() if isinstance(value, bool) else str(value)
        if row:
            row.config_value = str_value
        else:
            db.add(SiteConfig(config_key=key, config_value=str_value))
    await db.flush()
