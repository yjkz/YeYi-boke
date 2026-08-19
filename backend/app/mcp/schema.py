from pydantic import BaseModel, ConfigDict, Field

from app.modules.comments.schema import AdminCommentResponse, CommentCreateResponse
from app.modules.config.schema import SiteConfigResponse
from app.modules.posts.schema import (
    CategoryCreate,
    CategoryResponse,
    PostCreate,
    PostListItem,
    PostResponse,
    PostUpdate,
    TagCreate,
    TagResponse,
)


class MCPModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MCPPostCreate(PostCreate, MCPModel):
    title: str = Field(..., description="Post title", examples=["A practical FastAPI guide"])
    content_md: str = Field(default="", description="Markdown body")


class MCPPostUpdate(PostUpdate, MCPModel):
    content_md: str | None = Field(default=None, description="Replacement Markdown body")


class MCPCategoryCreate(CategoryCreate, MCPModel):
    name: str = Field(..., description="Display name")
    slug: str = Field(..., description="Unique URL slug")


class MCPTagCreate(TagCreate, MCPModel):
    name: str = Field(..., description="Display name")
    slug: str = Field(..., description="Unique URL slug")


class MCPCommentCreate(MCPModel):
    post_slug: str = Field(..., min_length=1, max_length=200, description="Target post slug")
    nickname: str = Field(..., min_length=1, max_length=50, description="Author display name")
    content: str = Field(..., min_length=1, max_length=2000, description="Comment body")
    email: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=200)
    parent_id: int | None = Field(default=None, ge=1)
    status: str | None = Field(default=None, pattern="^(pending|approved|rejected)$", description="Moderation status; omitted uses site setting")


class MCPConfigPatch(MCPModel):
    site_title: str | None = None
    site_subtitle: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    announcement: str | None = None
    about_content: str | None = None
    footer_text: str | None = None
    social_links: dict | None = None
    comment_enabled: bool | None = None
    comment_need_review: bool | None = None


class PostPage(MCPModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int
    count: int
    has_more: bool
    next_offset: int | None


class CategoryPage(MCPModel):
    items: list[CategoryResponse]
    total: int
    page: int
    page_size: int
    count: int
    has_more: bool
    next_offset: int | None


class TagPage(MCPModel):
    items: list[TagResponse]
    total: int
    page: int
    page_size: int
    count: int
    has_more: bool
    next_offset: int | None


class CommentPage(MCPModel):
    items: list[AdminCommentResponse]
    total: int
    page: int
    page_size: int
    count: int
    has_more: bool
    next_offset: int | None


class DeletePostResult(MCPModel):
    deleted: bool
    post_id: int
    status: str = "deleted"


class DeleteCategoryResult(MCPModel):
    deleted: bool
    category_id: int
    status: str = "deleted"


class DeleteTagResult(MCPModel):
    deleted: bool
    tag_id: int
    status: str = "deleted"


class DeleteCommentResult(MCPModel):
    deleted: bool
    comment_id: int
    status: str = "deleted"


class StatsOverview(MCPModel):
    today_pv: int
    total_posts: int
    total_comments: int


class StatsTrendItem(MCPModel):
    date: str
    page_views: int
    unique_visitors: int


class StatsTrend(MCPModel):
    data: list[StatsTrendItem]
    days: int


class UploadResult(MCPModel):
    url: str
    filename: str
    size: int


__all__ = [
    "MCPPostCreate", "MCPPostUpdate", "MCPCategoryCreate", "MCPTagCreate", "MCPCommentCreate",
    "MCPConfigPatch", "PostPage", "CategoryPage", "TagPage", "CommentPage", "DeletePostResult",
    "DeleteCategoryResult", "DeleteTagResult", "DeleteCommentResult", "StatsOverview", "StatsTrend",
    "StatsTrendItem", "UploadResult", "PostResponse", "CategoryResponse", "TagResponse", "CommentCreateResponse",
    "SiteConfigResponse",
]
