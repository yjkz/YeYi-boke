import asyncio

from app.database import async_session, engine, Base
from app.modules.users.model import User
from app.modules.config.model import SiteConfig
from app.utils.security import hash_password


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        from sqlalchemy import select
        existing = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not existing:
            admin = User(username="admin", password_hash=hash_password("admin123"), email="admin@yeyi.blog", role="admin")
            db.add(admin)
            print("Created admin user: admin / admin123")

        configs = [
            ("site_title", "YeYi 的博客"),
            ("site_subtitle", "记录生活与代码"),
            ("announcement", "欢迎来到我的博客！"),
            ("footer_text", "© 2026 YeYi"),
        ]
        for key, value in configs:
            existing = (await db.execute(select(SiteConfig).where(SiteConfig.config_key == key))).scalar_one_or_none()
            if not existing:
                db.add(SiteConfig(config_key=key, config_value=value))

        await db.commit()
        print("Seed data created.")


if __name__ == "__main__":
    asyncio.run(seed())
