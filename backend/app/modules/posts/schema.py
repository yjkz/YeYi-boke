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
    content_md: str | None
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
    updated_at: datetime
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
