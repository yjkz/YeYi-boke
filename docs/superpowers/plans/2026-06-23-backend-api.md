# Backend API 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 YeYi 博客的 FastAPI 后端 API，采用模块化单体架构，为后期微服务拆分做好准备。

**Architecture:** 模块化单体 FastAPI 应用，按业务域划分为 6 个模块（posts / comments / users / search / stats / config），每个模块独立的 router / service / model / schema。模块间通过 service 层调用，不直接访问其他模块的 model。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), asyncmy, Redis (redis-py), JWT (python-jose), bcrypt (passlib), Pydantic v2

## Global Constraints

- Python 3.11+，使用 async/await 异步模式
- SQLAlchemy 2.0+ 新风格（async session, Mapped, mapped_column）
- Pydantic v2（使用 model_validator 而非 validator）
- 所有 API 路径前缀 `/api/v1/`
- 数据库：MySQL 8.0+，字符集 utf8mb4
- 缓存：Redis 7+
- 认证：JWT (HS256)，access_token 2小时，refresh_token 7天
- 代码风格：无注释除非必要，函数名 snake_case，类名 PascalCase
- 每个模块必须可独立拆分为微服务（模块间只通过 service 层调用）

---

## 文件结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口，注册路由和中间件
│   ├── config.py                  # 全局配置（Pydantic Settings）
│   ├── database.py                # 异步数据库引擎和 session 工厂
│   ├── redis_client.py            # Redis 连接
│   ├── dependencies.py            # 公共依赖（get_db, get_current_user, pagination）
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors.py                # CORS 中间件配置
│   │   └── rate_limit.py          # Redis 限流中间件
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── posts/
│   │   │   ├── __init__.py        # 导出 router
│   │   │   ├── router.py          # API 路由
│   │   │   ├── service.py         # 业务逻辑
│   │   │   ├── model.py           # SQLAlchemy 模型（posts, categories, tags, post_tags）
│   │   │   └── schema.py          # Pydantic 请求/响应模型
│   │   ├── comments/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── model.py
│   │   │   └── schema.py
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── model.py
│   │   │   └── schema.py
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── service.py         # 搜索逻辑（调用 posts module 的 model）
│   │   ├── stats/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── model.py           # visit_logs, visit_stats
│   │   │   └── schema.py
│   │   └── config/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── model.py           # site_config
│   │       └── schema.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py            # JWT 编解码、密码哈希
│       └── markdown.py            # Markdown 渲染（markdown-it-py）
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
└── tests/
    ├── conftest.py                # 测试 fixtures（db session, test client, auth headers）
    ├── test_auth.py
    ├── test_posts.py
    ├── test_comments.py
    ├── test_search.py
    ├── test_stats.py
    └── test_config.py
```

---

## Task 1: 项目初始化与配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/redis_client.py`

**Interfaces:**
- Produces: `settings` (app.config.Settings), `get_db()` (async generator), `redis` (redis.asyncio.Redis)

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncmy==0.2.9
alembic==1.13.0
redis==5.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
feedgen==1.0.0
pydantic[email]==2.9.0
pydantic-settings==2.5.0
markdown-it-py==3.0.0
mdit-py-plugins==0.4.0
Pillow==10.4.0
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 2: 创建 config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "YeYi Blog API"
    DEBUG: bool = False

    DATABASE_URL: str = "mysql+asyncmy://root:root@localhost:3306/yeyi_blog"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 3: 创建 database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 4: 创建 redis_client.py**

```python
import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
```

- [ ] **Step 5: 创建 app/__init__.py**

```python
```

- [ ] **Step 6: 安装依赖并验证**

Run: `cd backend && pip install -r requirements.txt`
Expected: 安装成功，无报错

- [ ] **Step 7: Commit**

```bash
cd backend && git add -A && git commit -m "feat: project init with config, database, redis"
```

---

## Task 2: 安全工具（JWT + 密码）

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/security.py`

**Interfaces:**
- Produces:
  - `hash_password(password: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(data: dict) -> str`
  - `create_refresh_token(data: dict) -> str`
  - `decode_token(token: str) -> dict` — raises JWTError on invalid

- [ ] **Step 1: 创建 security.py**

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

- [ ] **Step 2: 创建 utils/__init__.py**

```python
```

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: add JWT and password utilities"
```

---

## Task 3: 公共依赖（认证、分页）

**Files:**
- Create: `backend/app/dependencies.py`

**Interfaces:**
- Produces:
  - `get_current_user(token, db) -> User` — 从 header 解析 JWT，查数据库返回用户
  - `Pagination` — 分页参数依赖

- [ ] **Step 1: 创建 dependencies.py**

```python
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.users.model import User
from app.utils.security import decode_token

security_scheme = HTTPBearer()


class Pagination:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 2: Commit**

```bash
cd backend && git add -A && git commit -m "feat: add auth dependency and pagination"
```

---

## Task 4: Users 模块（模型 + API）

**Files:**
- Create: `backend/app/modules/__init__.py`
- Create: `backend/app/modules/users/__init__.py`
- Create: `backend/app/modules/users/model.py`
- Create: `backend/app/modules/users/schema.py`
- Create: `backend/app/modules/users/service.py`
- Create: `backend/app/modules/users/router.py`

**Interfaces:**
- Produces:
  - `User` model（id, username, password_hash, email, avatar, role, created_at, updated_at）
  - `POST /api/v1/auth/login` → 返回 access_token + refresh_token
  - `POST /api/v1/auth/logout` → 失效 refresh_token
  - `POST /api/v1/auth/refresh` → 用 refresh_token 换新 access_token
  - `GET /api/v1/auth/me` → 返回当前用户信息

- [ ] **Step 1: 创建 model.py**

```python
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100))
    avatar: Mapped[str | None] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(Enum("admin", "editor", name="user_role"), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建 schema.py**

```python
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    avatar: str | None
    role: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 创建 service.py**

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import User
from app.utils.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.redis_client import redis_client


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def create_tokens(user: User) -> dict:
    payload = {"sub": user.id, "username": user.username, "role": user.role}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
    }


async def store_refresh_token(user_id: int, token: str) -> None:
    from app.config import settings
    ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
    await redis_client.set(f"refresh_token:{user_id}", token, ex=ttl)


async def invalidate_refresh_token(user_id: int) -> None:
    await redis_client.delete(f"refresh_token:{user_id}")


async def refresh_access_token(db: AsyncSession, token: str) -> dict:
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
    except Exception:
        raise ValueError("Invalid refresh token")

    user_id = payload.get("sub")
    stored = await redis_client.get(f"refresh_token:{user_id}")
    if stored != token:
        raise ValueError("Refresh token revoked")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    return create_tokens(user)
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.users.model import User
from app.modules.users.schema import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.modules.users.service import authenticate_user, create_tokens, invalidate_refresh_token, refresh_access_token, store_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    tokens = create_tokens(user)
    await store_refresh_token(user.id, tokens["refresh_token"])
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    await invalidate_refresh_token(current_user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await refresh_access_token(db, body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 5: 创建 __init__.py 文件**

```python
# modules/__init__.py
```

```python
# modules/users/__init__.py
from app.modules.users.router import router
```

- [ ] **Step 6: Commit**

```bash
cd backend && git add -A && git commit -m "feat: users module with auth endpoints"
```

---

## Task 5: Posts 模块（模型）

**Files:**
- Create: `backend/app/modules/posts/__init__.py`
- Create: `backend/app/modules/posts/model.py`

**Interfaces:**
- Produces: `Post`, `Category`, `Tag`, `post_tags` models — 被 posts service、comments module、search module 依赖

- [ ] **Step 1: 创建 model.py**

```python
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(secondary=post_tags, back_populates="tags")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    content_md: Mapped[str | None] = mapped_column(Text)
    content_html: Mapped[str | None] = mapped_column(Text)
    excerpt: Mapped[str | None] = mapped_column(String(500))
    cover_image: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(Enum("draft", "published", name="post_status"), default="draft")
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    category: Mapped["Category | None"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")
```

- [ ] **Step 2: 创建 __init__.py**

```python
from app.modules.posts.router import router
```

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: posts module models (Post, Category, Tag)"
```

---

## Task 6: Posts 模块（Schema + Service + Router）

**Files:**
- Create: `backend/app/modules/posts/schema.py`
- Create: `backend/app/modules/posts/service.py`
- Create: `backend/app/modules/posts/router.py`
- Modify: `backend/app/utils/markdown.py`

**Interfaces:**
- Produces:
  - `GET /api/v1/posts` — 文章列表（分页、按分类/标签筛选）
  - `GET /api/v1/posts/{slug}` — 文章详情（同时增加浏览量）
  - `POST /api/v1/admin/posts` — 创建文章
  - `PUT /api/v1/admin/posts/{id}` — 更新文章
  - `DELETE /api/v1/admin/posts/{id}` — 删除文章
  - `POST /api/v1/admin/posts/{id}/publish` — 发布
  - `POST /api/v1/admin/posts/{id}/draft` — 下架
  - `GET /api/v1/categories` — 分类列表
  - `GET /api/v1/tags` — 标签列表

- [ ] **Step 1: 创建 utils/markdown.py**

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

md = MarkdownIt("commonmark", {"html": True, "typographer": True})
md.enable("table")
front_matter_plugin(md)
footnote_plugin(md)


def render_markdown(text: str) -> str:
    return md.render(text)
```

- [ ] **Step 2: 创建 schema.py**

```python
from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    content_md: str = ""
    excerpt: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = []
    is_top: bool = False


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200)
    content_md: str | None = None
    excerpt: str | None = None
    cover_image: str | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None
    is_top: bool | None = None


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    sort_order: int

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content_html: str | None
    excerpt: str | None
    cover_image: str | None
    status: str
    category: CategoryResponse | None
    tags: list[TagResponse]
    view_count: int
    is_top: bool
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str | None
    cover_image: str | None
    status: str
    category: CategoryResponse | None
    tags: list[TagResponse]
    view_count: int
    is_top: bool
    created_at: datetime
    published_at: datetime | None

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    sort_order: int = 0


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
```

- [ ] **Step 3: 创建 service.py**

```python
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.posts.model import Category, Post, Tag, post_tags
from app.modules.posts.schema import PostCreate, PostUpdate
from app.utils.markdown import render_markdown


async def get_posts(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    category_slug: str | None = None,
    tag_slug: str | None = None,
    status: str = "published",
):
    query = select(Post).options(selectinload(Post.category), selectinload(Post.tags))
    query = query.where(Post.status == status)
    query = query.order_by(Post.is_top.desc(), Post.published_at.desc())

    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)
    if tag_slug:
        query = query.join(post_tags).join(Tag).where(Tag.slug == tag_slug)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    posts = result.scalars().unique().all()
    return posts, total


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags))
        .where(Post.slug == slug)
    )
    return result.scalar_one_or_none()


async def increment_view_count(db: AsyncSession, post: Post) -> None:
    post.view_count += 1
    await db.flush()


async def create_post(db: AsyncSession, data: PostCreate) -> Post:
    content_html = render_markdown(data.content_md) if data.content_md else ""
    excerpt = data.excerpt or (data.content_md[:200] if data.content_md else "")

    post = Post(
        title=data.title,
        slug=data.slug,
        content_md=data.content_md,
        content_html=content_html,
        excerpt=excerpt,
        cover_image=data.cover_image,
        category_id=data.category_id,
        is_top=data.is_top,
    )
    db.add(post)
    await db.flush()

    if data.tag_ids:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))).scalars().all()
        post.tags = tags

    await db.refresh(post, ["category", "tags"])
    return post


async def update_post(db: AsyncSession, post_id: int, data: PostUpdate) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    if "content_md" in update_data:
        update_data["content_html"] = render_markdown(update_data["content_md"])
        if "excerpt" not in update_data:
            update_data["excerpt"] = update_data["content_md"][:200]

    for key, value in update_data.items():
        setattr(post, key, value)

    if tag_ids is not None:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))).scalars().all()
        post.tags = tags

    await db.flush()
    await db.refresh(post, ["category", "tags"])
    return post


async def delete_post(db: AsyncSession, post_id: int) -> bool:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        return False
    await db.delete(post)
    await db.flush()
    return True


async def publish_post(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(post, ["category", "tags"])
    return post


async def draft_post(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    post.status = "draft"
    await db.flush()
    await db.refresh(post, ["category", "tags"])
    return post


async def get_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.sort_order, Category.id))
    return list(result.scalars().all())


async def create_category(db: AsyncSession, name: str, slug: str, description: str | None = None, sort_order: int = 0) -> Category:
    category = Category(name=name, slug=slug, description=description, sort_order=sort_order)
    db.add(category)
    await db.flush()
    return category


async def get_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.id))
    return list(result.scalars().all())


async def create_tag(db: AsyncSession, name: str, slug: str) -> Tag:
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    await db.flush()
    return tag
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, get_current_user
from app.modules.users.model import User
from app.modules.posts import service as post_service
from app.modules.posts.schema import (
    CategoryCreate, CategoryResponse, PostCreate, PostListResponse,
    PostResponse, PostUpdate, TagCreate, TagResponse,
)

router = APIRouter(tags=["posts"])


# ── Public ──

@router.get("/posts", response_model=PostListResponse)
async def list_posts(
    pagination: Pagination = Depends(),
    category: str | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    posts, total = await post_service.get_posts(db, offset=pagination.offset, limit=pagination.page_size, category_slug=category, tag_slug=tag)
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await post_service.increment_view_count(db, post)
    return post


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await post_service.get_categories(db)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await post_service.get_tags(db)


# ── Admin ──

@router.post("/admin/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_post(db, data)


@router.put("/admin/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, data: PostUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.update_post(db, post_id, data)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/admin/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not await post_service.delete_post(db, post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/admin/posts/{post_id}/publish", response_model=PostResponse)
async def publish_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.publish_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/posts/{post_id}/draft", response_model=PostResponse)
async def draft_post(post_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    post = await post_service.draft_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_category(db, data.name, data.slug, data.description, data.sort_order)


@router.post("/admin/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await post_service.create_tag(db, data.name, data.slug)
```

- [ ] **Step 5: Commit**

```bash
cd backend && git add -A && git commit -m "feat: posts module with CRUD, publish/draft, categories, tags"
```

---

## Task 7: Comments 模块

**Files:**
- Create: `backend/app/modules/comments/__init__.py`
- Create: `backend/app/modules/comments/model.py`
- Create: `backend/app/modules/comments/schema.py`
- Create: `backend/app/modules/comments/service.py`
- Create: `backend/app/modules/comments/router.py`

**Interfaces:**
- Produces:
  - `POST /api/v1/comments` — 提交评论（访客）
  - `GET /api/v1/posts/{slug}/comments` — 获取文章已审核评论（公开）
  - `GET /api/v1/admin/comments` — 评论管理列表（含待审核）
  - `PUT /api/v1/admin/comments/{id}` — 审核评论
  - `DELETE /api/v1/admin/comments/{id}` — 删除评论

- [ ] **Step 1: 创建 model.py**

```python
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Enum("pending", "approved", "rejected", name="comment_status"), default="pending")
    visitor_ip: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    post = relationship("Post", backref="comments")
    replies: Mapped[list["Comment"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    parent: Mapped["Comment | None"] = relationship(back_populates="replies", remote_side="Comment.id")
```

- [ ] **Step 2: 创建 schema.py**

```python
from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    post_slug: str
    parent_id: int | None = None
    nickname: str = Field(..., min_length=1, max_length=50)
    email: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")


class CommentResponse(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    nickname: str
    website: str | None
    content: str
    status: str
    created_at: datetime
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


class AdminCommentResponse(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    nickname: str
    email: str | None
    website: str | None
    content: str
    status: str
    visitor_ip: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCommentListResponse(BaseModel):
    items: list[AdminCommentResponse]
    total: int
    page: int
    page_size: int
```

- [ ] **Step 3: 创建 service.py**

```python
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.comments.model import Comment
from app.modules.posts.model import Post


async def create_comment(db: AsyncSession, post_slug: str, nickname: str, content: str, email: str | None = None, website: str | None = None, parent_id: int | None = None, visitor_ip: str | None = None) -> Comment | None:
    result = await db.execute(select(Post.id).where(Post.slug == post_slug))
    post_id = result.scalar_one_or_none()
    if not post_id:
        return None

    comment = Comment(
        post_id=post_id,
        parent_id=parent_id,
        nickname=nickname,
        email=email,
        website=website,
        content=content,
        visitor_ip=visitor_ip,
    )
    db.add(comment)
    await db.flush()
    return comment


async def get_approved_comments(db: AsyncSession, post_slug: str) -> list[Comment]:
    result = await db.execute(
        select(Post.id).where(Post.slug == post_slug)
    )
    post_id = result.scalar_one_or_none()
    if not post_id:
        return []

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.status == "approved", Comment.parent_id.is_(None))
        .order_by(Comment.created_at)
    )
    return list(result.scalars().all())


async def get_admin_comments(db: AsyncSession, offset: int = 0, limit: int = 20, status: str | None = None):
    query = select(Comment)
    if status:
        query = query.where(Comment.status == status)
    query = query.order_by(Comment.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def update_comment_status(db: AsyncSession, comment_id: int, status: str) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        return None
    comment.status = status
    await db.flush()
    return comment


async def delete_comment(db: AsyncSession, comment_id: int) -> bool:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        return False
    await db.delete(comment)
    await db.flush()
    return True
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, get_current_user
from app.modules.comments import service as comment_service
from app.modules.comments.schema import AdminCommentListResponse, CommentCreate, CommentResponse, CommentUpdate
from app.modules.users.model import User

router = APIRouter(tags=["comments"])


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentCreate, request: Request, db: AsyncSession = Depends(get_db)):
    comment = await comment_service.create_comment(
        db, post_slug=body.post_slug, nickname=body.nickname, content=body.content,
        email=body.email, website=body.website, parent_id=body.parent_id,
        visitor_ip=request.client.host if request.client else None,
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return comment


@router.get("/posts/{slug}/comments", response_model=list[CommentResponse])
async def get_comments(slug: str, db: AsyncSession = Depends(get_db)):
    return await comment_service.get_approved_comments(db, slug)


@router.get("/admin/comments", response_model=AdminCommentListResponse)
async def admin_list_comments(
    pagination: Pagination = Depends(),
    comment_status: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    items, total = await comment_service.get_admin_comments(db, offset=pagination.offset, limit=pagination.page_size, status=comment_status)
    return {"items": items, "total": total, "page": pagination.page, "page_size": pagination.page_size}


@router.put("/admin/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, body: CommentUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    comment = await comment_service.update_comment_status(db, comment_id, body.status)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/admin/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not await comment_service.delete_comment(db, comment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
```

- [ ] **Step 5: 创建 __init__.py**

```python
from app.modules.comments.router import router
```

- [ ] **Step 6: Commit**

```bash
cd backend && git add -A && git commit -m "feat: comments module with create, review, admin management"
```

---

## Task 8: Config 模块（站点配置）

**Files:**
- Create: `backend/app/modules/config/__init__.py`
- Create: `backend/app/modules/config/model.py`
- Create: `backend/app/modules/config/schema.py`
- Create: `backend/app/modules/config/service.py`
- Create: `backend/app/modules/config/router.py`

**Interfaces:**
- Produces:
  - `GET /api/v1/site/config` — 公开站点配置
  - `GET /api/v1/site/announcement` — 公告
  - `PUT /api/v1/admin/site/config` — 更新配置

- [ ] **Step 1: 创建 model.py**

```python
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SiteConfig(Base):
    __tablename__ = "site_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    config_value: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(200))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建 schema.py**

```python
from pydantic import BaseModel


class SiteConfigResponse(BaseModel):
    site_title: str = "YeYi 的博客"
    site_subtitle: str = ""
    logo_url: str = ""
    favicon_url: str = ""
    footer_text: str = ""
    social_links: dict = {}
    comment_enabled: bool = True
    comment_need_review: bool = True

    model_config = {"from_attributes": True}


class SiteConfigUpdate(BaseModel):
    site_title: str | None = None
    site_subtitle: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    footer_text: str | None = None
    social_links: dict | None = None
    comment_enabled: bool | None = None
    comment_need_review: bool | None = None


class AnnouncementResponse(BaseModel):
    content: str = ""
```

- [ ] **Step 3: 创建 service.py**

```python
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

    merged["comment_enabled"] = merged["comment_enabled"].lower() == "true"
    merged["comment_need_review"] = merged["comment_need_review"].lower() == "true"
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
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
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
async def update_site_config(body: SiteConfigUpdate, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    updates = body.model_dump(exclude_unset=True)
    await config_service.update_config(db, updates)
    return await config_service.get_all_config(db)
```

- [ ] **Step 5: 创建 __init__.py**

```python
from app.modules.config.router import router
```

- [ ] **Step 6: Commit**

```bash
cd backend && git add -A && git commit -m "feat: config module for site settings and announcement"
```

---

## Task 9: Search 模块

**Files:**
- Create: `backend/app/modules/search/__init__.py`
- Create: `backend/app/modules/search/service.py`
- Create: `backend/app/modules/search/router.py`

**Interfaces:**
- Produces:
  - `GET /api/v1/search?q=xxx` — 全文搜索文章

- [ ] **Step 1: 创建 service.py**

```python
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.posts.model import Post
from app.modules.posts.schema import PostListItem


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
```

- [ ] **Step 2: 创建 router.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination
from app.modules.search import service as search_service
from app.modules.posts.schema import PostListResponse

router = APIRouter(tags=["search"])


@router.get("/search", response_model=PostListResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    posts, total = await search_service.search_posts(db, q, offset=pagination.offset, limit=pagination.page_size)
    return {"items": posts, "total": total, "page": pagination.page, "page_size": pagination.page_size}
```

- [ ] **Step 3: 创建 __init__.py**

```python
from app.modules.search.router import router
```

- [ ] **Step 4: Commit**

```bash
cd backend && git add -A && git commit -m "feat: search module with LIKE-based full text search"
```

---

## Task 10: Stats 模块

**Files:**
- Create: `backend/app/modules/stats/__init__.py`
- Create: `backend/app/modules/stats/model.py`
- Create: `backend/app/modules/stats/schema.py`
- Create: `backend/app/modules/stats/service.py`
- Create: `backend/app/modules/stats/router.py`

**Interfaces:**
- Produces:
  - `POST /api/v1/visit` — 记录访问
  - `GET /api/v1/admin/stats` — 概览（今日PV、总文章数、总评论数）
  - `GET /api/v1/admin/stats/trend` — 趋势（最近N天PV曲线）

- [ ] **Step 1: 创建 model.py**

```python
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VisitLog(Base):
    __tablename__ = "visit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    page_path: Mapped[str] = mapped_column(String(500), nullable=False)
    page_title: Mapped[str | None] = mapped_column(String(200))
    visitor_ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    referer: Mapped[str | None] = mapped_column(String(500))
    country: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class VisitStats(Base):
    __tablename__ = "visit_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    top_pages: Mapped[dict | None] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建 schema.py**

```python
from pydantic import BaseModel


class VisitRequest(BaseModel):
    page_path: str
    page_title: str | None = None


class StatsOverview(BaseModel):
    today_pv: int
    total_posts: int
    total_comments: int


class TrendPoint(BaseModel):
    date: str
    page_views: int
    unique_visitors: int


class StatsTrendResponse(BaseModel):
    data: list[TrendPoint]
```

- [ ] **Step 3: 创建 service.py**

```python
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
        select(VisitStats)
        .where(VisitStats.stat_date >= start_date)
        .order_by(VisitStats.stat_date)
    )
    return [
        {"date": str(row.stat_date), "page_views": row.page_views, "unique_visitors": row.unique_visitors}
        for row in result.scalars().all()
    ]
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.stats import service as stats_service
from app.modules.stats.schema import StatsOverview, StatsTrendResponse, VisitRequest
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


@router.get("/admin/stats", response_model=StatsOverview)
async def get_overview(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    return await stats_service.get_stats_overview(db)


@router.get("/admin/stats/trend", response_model=StatsTrendResponse)
async def get_trend(days: int = Query(7, ge=1, le=90), db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    data = await stats_service.get_stats_trend(db, days)
    return {"data": data}
```

- [ ] **Step 5: 创建 __init__.py**

```python
from app.modules.stats.router import router
```

- [ ] **Step 6: Commit**

```bash
cd backend && git add -A && git commit -m "feat: stats module with visit tracking and trend API"
```

---

## Task 11: 中间件（CORS + 限流）

**Files:**
- Create: `backend/app/middleware/__init__.py`
- Create: `backend/app/middleware/cors.py`
- Create: `backend/app/middleware/rate_limit.py`

**Interfaces:**
- Produces: `setup_cors(app)` 和 `rate_limit(limit, window)` 依赖

- [ ] **Step 1: 创建 cors.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

- [ ] **Step 2: 创建 rate_limit.py**

```python
from fastapi import HTTPException, Request, status

from app.redis_client import redis_client


def rate_limit(limit: int, window: int):
    async def dependency(request: Request):
        ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{ip}"
        current = await redis_client.get(key)
        if current is not None and int(current) >= limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
    return dependency
```

- [ ] **Step 3: 创建 __init__.py**

```python
```

- [ ] **Step 4: Commit**

```bash
cd backend && git add -A && git commit -m "feat: CORS and rate limit middleware"
```

---

## Task 12: 应用入口与路由注册

**Files:**
- Create: `backend/app/main.py`

**Interfaces:**
- Produces: FastAPI app 实例，所有路由注册完毕

- [ ] **Step 1: 创建 main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.middleware.cors import setup_cors
from app.modules.users.router import router as auth_router
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
app.include_router(posts_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: 验证服务启动**

Run: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
Expected: 服务启动，访问 http://localhost:8000/health 返回 `{"status":"ok"}`，访问 http://localhost:8000/docs 显示 Swagger 文档

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: app entry point with all routers registered"
```

---

## Task 13: Alembic 数据库迁移

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

**Interfaces:**
- Produces: 可用的数据库迁移工具

- [ ] **Step 1: 初始化 Alembic**

Run: `cd backend && alembic init alembic`
Expected: 生成 alembic/ 目录和 alembic.ini

- [ ] **Step 2: 修改 alembic/env.py**

替换 `alembic/env.py` 为：

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.database import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: 生成初始迁移**

Run: `cd backend && alembic revision --autogenerate -m "initial tables"`
Expected: 生成迁移文件，包含所有表的创建

- [ ] **Step 4: 执行迁移**

Run: `cd backend && alembic upgrade head`
Expected: 所有表创建成功

- [ ] **Step 5: Commit**

```bash
cd backend && git add -A && git commit -m "feat: alembic database migration setup"
```

---

## Task 14: 图片上传

**Files:**
- Modify: `backend/app/modules/users/service.py` — 添加 upload 逻辑
- Modify: `backend/app/modules/users/router.py` — 添加独立的 admin_router
- Modify: `backend/app/modules/users/__init__.py` — 导出 admin_router
- Modify: `backend/app/main.py` — 注册 admin_router

**Interfaces:**
- Produces:
  - `POST /api/v1/admin/upload` — 上传图片，返回 URL

- [ ] **Step 1: 在 service.py 中添加上传函数**

在 `backend/app/modules/users/service.py` 末尾添加：

```python
import os
import uuid

from fastapi import UploadFile

from app.config import settings


async def upload_image(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise ValueError("File too large")

    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"
```

- [ ] **Step 2: 在 router.py 中添加 admin_router**

在 `backend/app/modules/users/router.py` 末尾添加一个新的 router（前缀 `/admin`，不是 `/auth/admin`）：

```python
from fastapi import UploadFile, File

from app.modules.users.service import upload_image

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/upload")
async def upload(file: UploadFile = File(...), _user: User = Depends(get_current_user)):
    try:
        url = await upload_image(file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"url": url}
```

- [ ] **Step 3: 更新 __init__.py 导出 admin_router**

```python
from app.modules.users.router import router, admin_router
```

- [ ] **Step 4: 在 main.py 中注册 admin_router**

在 `app.include_router(auth_router, ...)` 后面添加：

```python
from app.modules.users.router import admin_router as users_admin_router

app.include_router(users_admin_router, prefix="/api/v1")
```

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: image upload endpoint"
```

---

## Task 15: RSS 订阅

**Files:**
- Create: `backend/app/modules/posts/rss.py`
- Modify: `backend/app/modules/posts/router.py` — 添加 RSS 路由

- [ ] **Step 1: 创建 rss.py**

```python
from datetime import datetime

from feedgen.feed import FeedGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.config.service import get_all_config
from app.modules.posts.model import Post


async def generate_rss(db: AsyncSession) -> str:
    config = await get_all_config(db)
    fg = FeedGenerator()
    fg.title(config.get("site_title", "YeYi Blog"))
    fg.link(href="http://localhost:3000")
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
        fe.link(href=f"http://localhost:3000/posts/{post.slug}")
        fe.description(post.excerpt or "")
        if post.published_at:
            fe.pubDate(post.published_at.replace(tzinfo=None))

    return fg.rss_str(pretty=True).decode("utf-8")
```

- [ ] **Step 2: 在 router.py 中添加 RSS 路由**

在 `backend/app/modules/posts/router.py` 的公开路由部分添加：

```python
from fastapi.responses import Response
from app.modules.posts.rss import generate_rss


@router.get("/rss.xml")
async def rss(db: AsyncSession = Depends(get_db)):
    xml = await generate_rss(db)
    return Response(content=xml, media_type="application/rss+xml")
```

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: RSS feed generation"
```

---

## Task 16: 测试

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_posts.py`
- Create: `backend/tests/test_comments.py`

**Interfaces:**
- Produces: 核心功能的集成测试

- [ ] **Step 1: 创建 conftest.py**

```python
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.modules.users.model import User
from app.utils.security import hash_password

TEST_DATABASE_URL = "mysql+asyncmy://root:root@localhost:3306/yeyi_blog_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(username="admin", password_hash=hash_password("admin123"), role="admin")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, admin_user: User) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

- [ ] **Step 2: 创建 test_auth.py**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 403
```

- [ ] **Step 3: 创建 test_posts.py**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers):
    resp = await client.post("/api/v1/admin/posts", json={
        "title": "Test Post",
        "slug": "test-post",
        "content_md": "# Hello\n\nThis is a test.",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Post"
    assert "<h1>" in data["content_html"]


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, auth_headers):
    await client.post("/api/v1/admin/posts", json={"title": "Post 1", "slug": "post-1", "content_md": "content"}, headers=auth_headers)
    resp = await client.get("/api/v1/posts")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0  # draft, not published


@pytest.mark.asyncio
async def test_publish_post(client: AsyncClient, auth_headers):
    create_resp = await client.post("/api/v1/admin/posts", json={"title": "Pub", "slug": "pub", "content_md": "hi"}, headers=auth_headers)
    post_id = create_resp.json()["id"]
    resp = await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"

    list_resp = await client.get("/api/v1/posts")
    assert list_resp.json()["total"] == 1
```

- [ ] **Step 4: 创建 test_comments.py**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, auth_headers):
    # Create and publish a post first
    create_resp = await client.post("/api/v1/admin/posts", json={"title": "C", "slug": "c", "content_md": "x"}, headers=auth_headers)
    post_id = create_resp.json()["id"]
    await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)

    resp = await client.post("/api/v1/comments", json={
        "post_slug": "c",
        "nickname": "visitor",
        "content": "nice post!",
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_admin_approve_comment(client: AsyncClient, auth_headers):
    create_resp = await client.post("/api/v1/admin/posts", json={"title": "C2", "slug": "c2", "content_md": "x"}, headers=auth_headers)
    post_id = create_resp.json()["id"]
    await client.post(f"/api/v1/admin/posts/{post_id}/publish", headers=auth_headers)

    comment_resp = await client.post("/api/v1/comments", json={"post_slug": "c2", "nickname": "v", "content": "hello"})
    comment_id = comment_resp.json()["id"]

    resp = await client.put(f"/api/v1/admin/comments/{comment_id}", json={"status": "approved"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
```

- [ ] **Step 5: 运行测试**

Run: `cd backend && pytest tests/ -v`
Expected: 所有测试通过

- [ ] **Step 6: Commit**

```bash
cd backend && git add -A && git commit -m "test: add integration tests for auth, posts, comments"
```

---

## Task 17: 创建管理员种子数据

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: 创建 seed.py**

```python
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
```

- [ ] **Step 2: 运行种子数据**

Run: `cd backend && python seed.py`
Expected: 输出 "Created admin user: admin / admin123" 和 "Seed data created."

- [ ] **Step 3: Commit**

```bash
cd backend && git add -A && git commit -m "feat: seed script for admin user and default config"
```
