import base64
import binascii
import asyncio
import functools
import logging
import os
import re
import time
from contextlib import asynccontextmanager
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import async_session
from app.mcp.auth import MCPAuthRateLimitMiddleware
from app.mcp.context import request_context
from app.modules.mcp import service as mcp_management
from app.modules.comments import service as comment_service
from app.modules.comments.schema import AdminCommentResponse, CommentCreateResponse
from app.modules.config import service as config_service
from app.modules.config.schema import SiteConfigResponse
from app.modules.posts import service as post_service
from app.modules.posts.schema import (
    CategoryResponse,
    PostListItem,
    PostResponse,
    TagResponse,
)
from app.modules.stats import service as stats_service
from app.modules.users.service import ALLOWED_IMAGE_EXTENSIONS, upload_image_bytes
from app.mcp.schema import (
    CategoryPage, CommentPage, DeleteCategoryResult, DeleteCommentResult, DeletePostResult,
    DeleteTagResult, MCPCommentCreate, MCPCategoryCreate, MCPConfigPatch, MCPPostCreate,
    MCPPostUpdate, MCPTagCreate, PostPage, StatsOverview, StatsTrend, TagPage, UploadResult,
)

logger = logging.getLogger("yeyi.mcp")

mcp = FastMCP(
    "yeyi_blog_mcp",
    instructions="Manage YeYi Blog content, comments, taxonomy, settings, statistics, and uploads.",
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    host=settings.MCP_HOST,
    port=settings.MCP_PORT,
    # mcp SDK 1.29+ 默认请求体上限 4MiB，会在应用层拦截 5MB 图片经 base64 膨胀后的请求体
    # （约 6.7MB），必须与上传上限对齐：base64 膨胀后体积 + 64KB JSON 包络余量
    # （MAX_UPLOAD_SIZE=5MB 时约 7.05MB，仍低于网关 12m，保持「应用层先拒绝并返回干净
    # 错误、网关兜底」的层次）。
    max_request_body_size=((settings.MAX_UPLOAD_SIZE + 2) // 3) * 4 + 64 * 1024,
)

READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
IDEMPOTENT_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)


@asynccontextmanager
async def db_session():
    async with async_session() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


def audited(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        started = time.perf_counter()
        context = request_context.get()
        tool_name = f"yeyi_blog_{func.__name__}"
        try:
            result = await func(*args, **kwargs)
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info("mcp_tool_call tool=%s success=true duration_ms=%s", tool_name, duration_ms)
            await _record_tool_log(context, tool_name, kwargs, True, duration_ms, None)
            return result
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info("mcp_tool_call tool=%s success=false duration_ms=%s", tool_name, duration_ms)
            await _record_tool_log(context, tool_name, kwargs, False, duration_ms, str(exc))
            raise

    return wrapper


async def _record_tool_log(context, tool_name: str, kwargs: dict, success: bool, duration_ms: int, error: str | None) -> None:
    if context is None:
        return
    resource_type = resource_id = resource_slug = None
    ids = {
        "post_id": "post",
        "category_id": "category",
        "tag_id": "tag",
        "comment_id": "comment",
    }
    for field, kind in ids.items():
        if kwargs.get(field) is not None:
            resource_type, resource_id = kind, str(kwargs[field])
            break
    data = kwargs.get("data")
    if data is not None:
        if getattr(data, "post_slug", None):
            resource_type, resource_slug = "post", data.post_slug
        elif getattr(data, "slug", None):
            resource_slug = data.slug
    try:
        await asyncio.wait_for(mcp_management.record_request_log(
            request_id=context.request_id,
            client_ip=context.client_ip,
            user_agent=context.user_agent,
            rpc_method="tools/call",
            tool_name=tool_name,
            success=success,
            http_status=200,
            duration_ms=duration_ms,
            error_message=error[:500] if error else None,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_slug=resource_slug,
            key_id=context.api_key_id,
            key_name=context.api_key_name,
            key_fingerprint=context.api_key_fingerprint,
        ), timeout=1.0)
    except Exception:
        logger.warning("mcp_audit_log_write_failed")


def dump(model: Any, value: Any) -> dict[str, Any]:
    return model.model_validate(value).model_dump(mode="json")


def validate_page(page: int, page_size: int) -> None:
    if page < 1 or page_size < 1 or page_size > 100:
        raise ValueError("page must be >= 1 and page_size must be between 1 and 100")


def validate_days(days: int) -> None:
    if days < 1 or days > 90:
        raise ValueError("days must be between 1 and 90")


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health(_: Request):
    return JSONResponse({"status": "ok"})


@mcp.tool(name="yeyi_blog_list_posts", description="List posts, including drafts. Use status to filter; page/page_size control pagination. The response includes next_offset and has_more.", annotations=READ, structured_output=True)
@audited
async def list_posts(status: Literal["draft", "published"] | None = None, page: int = 1, page_size: int = 10) -> PostPage:
    validate_page(page, page_size)
    async with db_session() as db:
        posts, total = await post_service.get_posts(db, offset=(page - 1) * page_size, limit=page_size, status=status)
        count = len(posts)
        return PostPage(items=[dump(PostListItem, post) for post in posts], total=total, page=page, page_size=page_size, count=count, has_more=(page - 1) * page_size + count < total, next_offset=(page * page_size if (page - 1) * page_size + count < total else None))


@mcp.tool(name="yeyi_blog_get_post", description="Get one post by numeric id or slug. Provide exactly one selector. If not found, list posts to verify the identifier.", annotations=READ, structured_output=True)
@audited
async def get_post(post_id: int | None = None, slug: str | None = None) -> PostResponse:
    if (post_id is None) == (slug is None):
        raise ValueError("Provide exactly one of post_id or slug")
    async with db_session() as db:
        post = await post_service.get_post_by_id(db, post_id) if post_id is not None else await post_service.get_post_by_slug(db, slug or "")
        if not post:
            raise ValueError("Post not found; use yeyi_blog_list_posts or verify post_id/slug")
        return dump(PostResponse, post)


@mcp.tool(name="yeyi_blog_create_post", description="Create a new draft post. Slug is generated when omitted; duplicate slugs fail with a recovery hint.", annotations=WRITE, structured_output=True)
@audited
async def create_post(data: MCPPostCreate) -> PostResponse:
    async with db_session() as db:
        try:
            return dump(PostResponse, await post_service.create_post(db, data))
        except IntegrityError as exc:
            raise ValueError("Slug already exists; use yeyi_blog_list_posts or choose a unique slug") from exc


@mcp.tool(name="yeyi_blog_update_post", description="Update an existing post. Only supplied fields change; changing content_md also regenerates HTML.", annotations=WRITE, structured_output=True)
@audited
async def update_post(post_id: int, data: MCPPostUpdate) -> PostResponse:
    async with db_session() as db:
        try:
            post = await post_service.update_post(db, post_id, data)
        except IntegrityError as exc:
            raise ValueError("Slug already exists; choose a unique slug or inspect posts") from exc
        if not post:
            raise ValueError("Post not found; use yeyi_blog_list_posts to verify post_id")
        return dump(PostResponse, post)


@mcp.tool(name="yeyi_blog_delete_post", description="Delete exactly one post. This destructive operation requires confirm=true and cannot be undone.", annotations=DESTRUCTIVE, structured_output=True)
@audited
async def delete_post(post_id: int, confirm: bool = False) -> DeletePostResult:
    if not confirm:
        raise ValueError("Deletion requires confirm=true")
    async with db_session() as db:
        if not await post_service.delete_post(db, post_id):
            raise ValueError("Post not found; use yeyi_blog_list_posts to verify post_id")
    return DeletePostResult(deleted=True, post_id=post_id)


@mcp.tool(name="yeyi_blog_publish_post", description="Publish one post immediately. Verify the post first when the ID is uncertain.", annotations=IDEMPOTENT_WRITE, structured_output=True)
@audited
async def publish_post(post_id: int) -> PostResponse:
    async with db_session() as db:
        post = await post_service.publish_post(db, post_id)
        if not post:
            raise ValueError("Post not found; use yeyi_blog_list_posts to verify post_id")
        return dump(PostResponse, post)


@mcp.tool(name="yeyi_blog_draft_post", description="Move one published post back to draft.", annotations=IDEMPOTENT_WRITE, structured_output=True)
@audited
async def draft_post(post_id: int) -> PostResponse:
    async with db_session() as db:
        post = await post_service.draft_post(db, post_id)
        if not post:
            raise ValueError("Post not found; use yeyi_blog_list_posts to verify post_id")
        return dump(PostResponse, post)


@mcp.tool(name="yeyi_blog_list_categories", description="List categories with pagination metadata.", annotations=READ, structured_output=True)
@audited
async def list_categories(page: int = 1, page_size: int = 50) -> CategoryPage:
    validate_page(page, page_size)
    async with db_session() as db:
        items, total = await post_service.get_categories_page(db, offset=(page - 1) * page_size, limit=page_size)
        count = len(items)
        return CategoryPage(items=[dump(CategoryResponse, value) for value in items], total=total, page=page, page_size=page_size, count=count, has_more=(page - 1) * page_size + count < total, next_offset=(page * page_size if (page - 1) * page_size + count < total else None))


@mcp.tool(name="yeyi_blog_create_category", description="Create a category with a unique slug.", annotations=WRITE, structured_output=True)
@audited
async def create_category(data: MCPCategoryCreate) -> CategoryResponse:
    async with db_session() as db:
        try:
            value = await post_service.create_category(db, data.name, data.slug, data.description, data.sort_order)
        except IntegrityError as exc:
            raise ValueError("Category slug already exists; use yeyi_blog_list_categories or choose a unique slug") from exc
        return dump(CategoryResponse, value)


@mcp.tool(name="yeyi_blog_update_category", description="Update one category by ID.", annotations=WRITE, structured_output=True)
@audited
async def update_category(category_id: int, data: MCPCategoryCreate) -> CategoryResponse:
    async with db_session() as db:
        try:
            value = await post_service.update_category(db, category_id, data.name, data.slug, data.description, data.sort_order)
        except IntegrityError as exc:
            raise ValueError("Category slug already exists; choose a unique slug") from exc
        if not value:
            raise ValueError("Category not found; use yeyi_blog_list_categories to verify category_id")
        return dump(CategoryResponse, value)


@mcp.tool(name="yeyi_blog_delete_category", description="Delete exactly one category. Requires confirm=true.", annotations=DESTRUCTIVE, structured_output=True)
@audited
async def delete_category(category_id: int, confirm: bool = False) -> DeleteCategoryResult:
    if not confirm:
        raise ValueError("Deletion requires confirm=true")
    async with db_session() as db:
        if not await post_service.delete_category(db, category_id):
            raise ValueError("Category not found; use yeyi_blog_list_categories to verify category_id")
    return DeleteCategoryResult(deleted=True, category_id=category_id)


@mcp.tool(name="yeyi_blog_list_tags", description="List tags with pagination metadata.", annotations=READ, structured_output=True)
@audited
async def list_tags(page: int = 1, page_size: int = 50) -> TagPage:
    validate_page(page, page_size)
    async with db_session() as db:
        items, total = await post_service.get_tags_page(db, offset=(page - 1) * page_size, limit=page_size)
        count = len(items)
        return TagPage(items=[dump(TagResponse, value) for value in items], total=total, page=page, page_size=page_size, count=count, has_more=(page - 1) * page_size + count < total, next_offset=(page * page_size if (page - 1) * page_size + count < total else None))


@mcp.tool(name="yeyi_blog_create_tag", description="Create a tag with a unique slug.", annotations=WRITE, structured_output=True)
@audited
async def create_tag(data: MCPTagCreate) -> TagResponse:
    async with db_session() as db:
        try:
            value = await post_service.create_tag(db, data.name, data.slug)
        except IntegrityError as exc:
            raise ValueError("Tag slug already exists; use yeyi_blog_list_tags or choose a unique slug") from exc
        return dump(TagResponse, value)


@mcp.tool(name="yeyi_blog_update_tag", description="Update one tag by ID.", annotations=WRITE, structured_output=True)
@audited
async def update_tag(tag_id: int, data: MCPTagCreate) -> TagResponse:
    async with db_session() as db:
        try:
            value = await post_service.update_tag(db, tag_id, data.name, data.slug)
        except IntegrityError as exc:
            raise ValueError("Tag slug already exists; choose a unique slug") from exc
        if not value:
            raise ValueError("Tag not found; use yeyi_blog_list_tags to verify tag_id")
        return dump(TagResponse, value)


@mcp.tool(name="yeyi_blog_delete_tag", description="Delete exactly one tag. Requires confirm=true.", annotations=DESTRUCTIVE, structured_output=True)
@audited
async def delete_tag(tag_id: int, confirm: bool = False) -> DeleteTagResult:
    if not confirm:
        raise ValueError("Deletion requires confirm=true")
    async with db_session() as db:
        if not await post_service.delete_tag(db, tag_id):
            raise ValueError("Tag not found; use yeyi_blog_list_tags to verify tag_id")
    return DeleteTagResult(deleted=True, tag_id=tag_id)


@mcp.tool(name="yeyi_blog_list_comments", description="List comments, including pending and rejected comments, with pagination metadata.", annotations=READ, structured_output=True)
@audited
async def list_comments(status: Literal["pending", "approved", "rejected"] | None = None, page: int = 1, page_size: int = 20) -> CommentPage:
    validate_page(page, page_size)
    async with db_session() as db:
        items, total = await comment_service.get_admin_comments(db, offset=(page - 1) * page_size, limit=page_size, status=status)
        count = len(items)
        return CommentPage(items=[dump(AdminCommentResponse, value) for value in items], total=total, page=page, page_size=page_size, count=count, has_more=(page - 1) * page_size + count < total, next_offset=(page * page_size if (page - 1) * page_size + count < total else None))


@mcp.tool(name="yeyi_blog_create_comment", description="Add a comment as an administrator. If status is omitted, comment_need_review chooses pending or approved.", annotations=WRITE, structured_output=True)
@audited
async def create_comment(data: MCPCommentCreate) -> CommentCreateResponse:
    async with db_session() as db:
        config = await config_service.get_all_config(db)
        comment_status = data.status or ("pending" if config.get("comment_need_review", True) else "approved")
        comment = await comment_service.create_comment(
            db, post_slug=data.post_slug, nickname=data.nickname, content=data.content,
            email=data.email, website=data.website, parent_id=data.parent_id, status=comment_status,
        )
        if not comment:
            raise ValueError("Post not found; use yeyi_blog_list_posts or yeyi_blog_get_post to verify post_slug")
        return dump(CommentCreateResponse, comment)


@mcp.tool(name="yeyi_blog_update_comment_status", description="Update a comment moderation status to pending, approved, or rejected.", annotations=IDEMPOTENT_WRITE, structured_output=True)
@audited
async def update_comment_status(comment_id: int, status: Literal["pending", "approved", "rejected"]) -> CommentCreateResponse:
    async with db_session() as db:
        comment = await comment_service.update_comment_status(db, comment_id, status)
        if not comment:
            raise ValueError("Comment not found; use yeyi_blog_list_comments to verify comment_id")
        return dump(CommentCreateResponse, comment)


@mcp.tool(name="yeyi_blog_delete_comment", description="Delete exactly one comment. Requires confirm=true.", annotations=DESTRUCTIVE, structured_output=True)
@audited
async def delete_comment(comment_id: int, confirm: bool = False) -> DeleteCommentResult:
    if not confirm:
        raise ValueError("Deletion requires confirm=true")
    async with db_session() as db:
        if not await comment_service.delete_comment(db, comment_id):
            raise ValueError("Comment not found; use yeyi_blog_list_comments to verify comment_id")
    return DeleteCommentResult(deleted=True, comment_id=comment_id)


@mcp.tool(name="yeyi_blog_get_site_config", description="Read the complete merged site configuration.", annotations=READ, structured_output=True)
@audited
async def get_site_config() -> SiteConfigResponse:
    async with db_session() as db:
        return dump(SiteConfigResponse, await config_service.get_all_config(db))


@mcp.tool(name="yeyi_blog_update_site_config", description="Partially update site configuration and return the complete merged result. Only supplied fields change.", annotations=WRITE, structured_output=True)
@audited
async def update_site_config(data: MCPConfigPatch) -> SiteConfigResponse:
    async with db_session() as db:
        await config_service.update_config(db, data.model_dump(exclude_unset=True))
        return dump(SiteConfigResponse, await config_service.get_all_config(db))


@mcp.tool(name="yeyi_blog_get_stats_overview", description="Return current PV, published post count, and approved comment count.", annotations=READ, structured_output=True)
@audited
async def get_stats_overview() -> StatsOverview:
    async with db_session() as db:
        return StatsOverview.model_validate(await stats_service.get_stats_overview(db))


@mcp.tool(name="yeyi_blog_get_stats_trend", description="Return daily PV/UV trend for 1-90 days.", annotations=READ, structured_output=True)
@audited
async def get_stats_trend(days: int = 7) -> StatsTrend:
    validate_days(days)
    async with db_session() as db:
        return StatsTrend(data=await stats_service.get_stats_trend(db, days), days=days)


_DATA_URI_RE = re.compile(r"^data:[\w.+-]+/[\w.+-]+;base64,")


def _normalize_base64_payload(raw: str) -> str:
    """Strip an optional data URI prefix and all whitespace from a base64 payload."""
    payload = re.sub(r"\s+", "", raw)
    match = _DATA_URI_RE.match(payload)
    return payload[match.end():] if match else payload


def _strict_b64decode(text: str) -> bytes | None:
    try:
        return base64.b64decode(text, validate=True)
    except (ValueError, binascii.Error):
        return None


def decode_base64_payload(payload: str) -> bytes:
    """Decode a normalized base64 payload, tolerating URL-safe alphabets and missing padding."""
    candidates = [payload]
    if "-" in payload or "_" in payload:
        candidates.append(payload.replace("-", "+").replace("_", "/"))
    for candidate in candidates:
        decoded = _strict_b64decode(candidate)
        if decoded is None and len(candidate) % 4 in (2, 3):
            decoded = _strict_b64decode(candidate + "=" * (-len(candidate) % 4))
        if decoded is not None:
            return decoded
    raise ValueError("content_base64 is invalid")


@mcp.tool(
    name="yeyi_blog_upload_image",
    description=(
        "Upload an image from Base64 content. Filename must be a simple file name with an allowed image extension "
        f"({'/'.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}); decoded content must be at most {settings.MAX_UPLOAD_SIZE} bytes. "
        "content_base64 accepts standard or URL-safe base64 with optional padding, embedded whitespace or newlines, "
        "and an optional data URI prefix (data:image/png;base64,...). The base64 text is about 4/3 of the decoded "
        "size; the server request body limit is sized to accommodate any payload within the upload limit."
    ),
    annotations=WRITE,
    structured_output=True,
)
@audited
async def upload_image(filename: str, content_base64: str) -> UploadResult:
    if not filename or os.path.basename(filename) != filename or any(separator in filename for separator in ("/", "\\")) or filename in {".", ".."}:
        raise ValueError("filename must be a simple file name")
    max_encoded = ((settings.MAX_UPLOAD_SIZE + 2) // 3) * 4
    limit_error = f"content_base64 exceeds the {settings.MAX_UPLOAD_SIZE} byte upload limit"
    # cheap guard: fail fast on oversized raw payloads before whitespace normalization
    if len(content_base64) > max_encoded * 2:
        raise ValueError(limit_error)
    payload = _normalize_base64_payload(content_base64)
    if len(payload) > max_encoded:
        raise ValueError(limit_error)
    try:
        content = decode_base64_payload(payload)
    except ValueError as exc:
        raise ValueError("content_base64 is invalid") from exc
    if not content:
        raise ValueError("content_base64 is empty")
    try:
        url = await upload_image_bytes(content, filename)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    return UploadResult(url=url, filename=filename, size=len(content))


mcp_http_app = mcp.streamable_http_app()
mcp_http_app.add_middleware(MCPAuthRateLimitMiddleware)
