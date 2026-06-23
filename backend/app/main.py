from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.middleware.cors import setup_cors
from app.modules.users.router import router as auth_router
from app.modules.users.router import admin_router as users_admin_router
from app.modules.posts.router import router as posts_router
from app.modules.comments.router import router as comments_router
from app.modules.config.router import router as config_router
from app.modules.search.router import router as search_router
from app.modules.stats.router import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
setup_cors(app)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_admin_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
