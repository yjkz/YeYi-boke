# 04 API 参考

- **Base URL**：`/api/v1`（网关域名下同域访问；健康检查 `/health` 无前缀）
- **认证方式**：管理接口需 `Authorization: Bearer <access_token>`，且 `role=admin`
- **分页约定**：`?page=1&page_size=10`（page_size 上限 100）；MCP 列表响应统一 `{items, total, page, page_size, count, has_more, next_offset}`
- **通用错误**：400 参数/业务错误 · 401 未认证或 token 失效 · 403 权限不足（或评论关闭） · 404 不存在 · 409 slug 冲突 · 429 限流超限（登录/评论/搜索/上传已挂载，见 §5）

## 1. 认证 users（`/auth`）

| 方法 | 路径 | 认证 | 请求体/参数 | 成功响应 |
|------|------|------|-------------|----------|
| POST | `/auth/login` | 无 | `{username, password}` | `200 {access_token, refresh_token, token_type:"bearer"}`；错误 401 |
| POST | `/auth/logout` | Bearer | — | `204`（删除 Redis 中的 refresh token） |
| POST | `/auth/refresh` | 无 | `{refresh_token}` | `200` 新双 token；无效/已撤销 401 |
| GET | `/auth/me` | Bearer | — | `200 {id, username, email, avatar, role}` |
| PUT | `/auth/password` | Bearer | `{current_password, new_password}` | `200 {message}`；旧密码错 400 |

token 机制：access 120 分钟；refresh 7 天且存于 Redis（`refresh_token:{user_id}`），刷新采用旋转式（签发新对、旧 refresh 失效）。

## 2. 文章 posts（公开）

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/posts` | `page, page_size, category=<slug>, tag=<slug>, sort=default|latest` | 仅 published；默认排序为置顶优先、发布时间倒序；`sort=latest` 忽略置顶权重，严格按发布时间倒序（同时间按 id 倒序） |
| GET | `/posts/{slug}` | — | 详情（含 content_html、category、tags）；非 published 404；浏览量防刷按 `request.client.host` 去重（已知限制：网关反代后为网关 IP，全站每文每小时最多 +1） |
| GET | `/categories` | — | 全部分类，按 `sort_order, id` |
| GET | `/tags` | — | 全部标签，按 id |
| GET | `/rss.xml` | — | `application/rss+xml`，最近 20 篇已发布；接口保留，前台导航暂不显示入口 |

**PostResponse 字段**：`id, title, slug, content_md, content_html, excerpt, cover_image, status, category{id,name,slug,description,sort_order}|null, tags[{id,name,slug}], view_count, is_top, created_at, updated_at, published_at`。`excerpt` 为不含 Markdown 源标记的纯文本摘要，列表项 `PostListItem` 同上但**不含** content_md/content_html。

## 3. 文章管理（`/admin/*`，需 admin）

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| GET | `/admin/posts` | `?status=draft|published&page=` | 管理列表（含草稿） |
| GET | `/admin/posts/{id}` | — | 按 id 取详情（编辑回显用） |
| POST | `/admin/posts` | `PostCreate` | `201`；slug 冲突 409 |
| PUT | `/admin/posts/{id}` | `PostUpdate`（部分字段） | 未提供字段不变更 |
| DELETE | `/admin/posts/{id}` | — | `204` |
| POST | `/admin/posts/{id}/publish` | — | 置 published，写 published_at |
| POST | `/admin/posts/{id}/draft` | — | 下架为 draft |

**PostCreate**：`{title(必填1-200), slug?(缺省拼音生成), content_md?, excerpt?, cover_image?, category_id?, tag_ids?:[], is_top?:false}`。
**PostUpdate**：全部字段 Optional；`content_md` 变更时服务端重渲染 `content_html` 并在未显式传 excerpt 时重新提取纯文本摘要；显式 excerpt 也会清理 Markdown 标记。

Admin 编辑器自动保存复用上述 POST/PUT：新建页标题非空后创建 draft，已有 draft 按 2 秒防抖更新；已发布文章不会自动保存，需显式点击保存。自动保存不新增接口、请求字段或数据库表。`content_html` 已统一清洗，代码块保留语言 class，公式保留 `$ / $$` 语义标记。

## 4. 分类 / 标签管理（需 admin）

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| POST | `/admin/categories` | `{name, slug, description?, sort_order?}` | `201`；slug 冲突 409 |
| PUT | `/admin/categories/{id}` | 同上 | `200`；404 |
| DELETE | `/admin/categories/{id}` | — | `204`；其下文章 category 置 NULL |
| POST | `/admin/tags` | `{name, slug}` | `201` |
| PUT | `/admin/tags/{id}` | 同上 | `200` |
| DELETE | `/admin/tags/{id}` | — | `204` |

## 5. 评论 comments

| 方法 | 路径 | 认证 | 请求体/参数 | 说明 |
|------|------|------|-------------|------|
| POST | `/comments` | 无 | `{post_slug, nickname(1-50), content(1-2000), email?, website?, parent_id?}` | `201`；站点配置 `comment_enabled=false` 时 403；文章不存在 404；落库为 **pending** |
| GET | `/posts/{slug}/comments` | 无 | — | 已批准顶级评论数组，每条含 `replies[]` |
| GET | `/admin/comments` | admin | `?status=&post_title=&page=&page_size=` | 分页管理列表（含 pending/rejected），响应含 `post_title`、`post_slug` |
| PUT | `/admin/comments/{id}` | admin | `{status: "approved"|"rejected"}` | 审核；REST 不支持传 `pending`（422），改回待审仅 MCP 工具 `yeyi_blog_update_comment_status` 支持 |
| DELETE | `/admin/comments/{id}` | admin | — | `204` |

**CommentResponse**：`id, post_id, parent_id, nickname, email, website, content, status, created_at, replies[]`。

评论创建时如果传入 `parent_id`，父评论必须存在且属于同一篇文章，否则返回 `400`。公开评论接口按 IP 限制为每分钟 5 次；搜索每分钟 30 次；登录每分钟 10 次；管理员上传每小时 50 次。限流 IP 优先取 `X-Real-IP`，其次取 `X-Forwarded-For` 首个地址。

## 6. 搜索 search

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/search` | `q`(必填 1-100), `page, page_size` | `LIKE` 匹配标题/正文/摘要，仅已发布，按发布时间倒序；响应同 `PostListResponse` |

## 7. 访问统计 stats

| 方法 | 路径 | 认证 | 请求体/参数 | 响应 |
|------|------|------|-------------|------|
| POST | `/visit` | 无 | `{page_path, page_title?}`（IP/UA/Referer 自动采集） | `204` |
| GET | `/admin/stats` | admin | — | `{today_pv, total_posts, total_comments}` |
| GET | `/admin/stats/trend` | admin | `days`(1-90, 默认7) | `{data: [{date, page_views, unique_visitors}]}` |

## 8. 站点配置 config

| 方法 | 路径 | 认证 | 请求体 | 说明 |
|------|------|------|--------|------|
| GET | `/site/config` | 无 | — | 全量配置（默认值合并；`comment_enabled/comment_need_review` 为 bool，`social_links` 为对象） |
| GET | `/site/announcement` | 无 | — | `{content: string}` |
| PUT | `/admin/site/config` | admin | 任意配置键的部分对象 | upsert 后返回全量配置 |

配置键清单：`site_title, site_subtitle, logo_url, avatar_url, favicon_url, announcement, about_content, footer_text, social_links, comment_enabled, comment_need_review`。

## 9. 上传与静态资源（需 admin）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/admin/upload` | `multipart/form-data`，字段名 `file`；扩展名仅允许 `.png/.jpg/.jpeg/.gif/.webp/.ico`（大小写不敏感），其余返回 400 `unsupported image type: <ext>`；uuid 重命名落盘 `uploads/`；>5MB 返回 400；响应 `{url: "/uploads/xxx.png"}` |
| GET | `/uploads/{filename}` | 静态文件服务（FastAPI StaticFiles / Nginx 反代） |
| GET | `/health`（无 `/api/v1` 前缀） | `{status: "ok"}`，健康检查 |

## 10. 交互式文档

FastAPI 自动生成：`/docs`（Swagger UI）与 `/redoc`。本地启动 backend 后访问 `http://localhost:8000/docs` 可直接调试全部端点。

## 11. MCP 管理接口

MCP 独立入口：`https://blogmcp.yeyeyiyi.online/mcp`。客户端可使用 `https://blogmcp.yeyeyiyi.online/mcp?tavilyApiKey=<key>` 接入，也支持 `?api_key=<key>` 查询参数或 `X-MCP-API-Key` 请求头；使用 Streamable HTTP transport。

可用工具（均带 `yeyi_blog_` 前缀，并通过 MCP ToolAnnotations 标记只读/幂等/破坏性行为）：

- 文章：`yeyi_blog_list_posts`、`yeyi_blog_get_post`、`yeyi_blog_create_post`、`yeyi_blog_update_post`、`yeyi_blog_delete_post`、`yeyi_blog_publish_post`、`yeyi_blog_draft_post`
- 分类/标签：`yeyi_blog_list_categories`、`yeyi_blog_create_category`、`yeyi_blog_update_category`、`yeyi_blog_delete_category`、`yeyi_blog_list_tags`、`yeyi_blog_create_tag`、`yeyi_blog_update_tag`、`yeyi_blog_delete_tag`
- 评论：`yeyi_blog_list_comments`、`yeyi_blog_create_comment`、`yeyi_blog_update_comment_status`、`yeyi_blog_delete_comment`
- 配置/统计：`yeyi_blog_get_site_config`、`yeyi_blog_update_site_config`、`yeyi_blog_get_stats_overview`、`yeyi_blog_get_stats_trend`
- 上传：`yeyi_blog_upload_image(filename, content_base64)`；`content_base64` 接受标准/URL-safe 字母表、可缺省 padding，可含换行/空白与 `data:image/*;base64,` 前缀；解码前按 `MAX_UPLOAD_SIZE`（默认 5MB）限制；`filename` 扩展名仅允许 `.png/.jpg/.jpeg/.gif/.webp/.ico`，其余报 `unsupported image type`

删除工具均要求 `confirm=true`。评论未显式指定状态时遵循 `comment_need_review` 配置。

客户端配置示例：

```json
{
  "mcpServers": {
    "yeyi-blog": {
      "url": "https://blogmcp.yeyeyiyi.online/mcp?tavilyApiKey=替换为实际密钥"
    }
  }
}
```

### MCP 后台管理 API

以下接口均需要现有 admin JWT：

- `GET /api/v1/admin/mcp/overview`：服务状态、地址、Key 摘要、限流和近 24 小时调用统计。
- `GET/PUT /api/v1/admin/mcp/settings`：读取或更新服务设置。
- `GET/POST /api/v1/admin/mcp/keys`、`PATCH/DELETE /api/v1/admin/mcp/keys/{key_id}`：管理多个 Key；创建请求中的 `api_key` 只写入不返回。
- `GET /api/v1/admin/mcp/keys/{key_id}/export-url`：管理员生成当前 Key 的 MCP 接入地址，用于复制到客户端配置。
- `GET /api/v1/admin/mcp/logs`：按页查询审计日志，可按工具名、成功状态、IP、Key 和起止时间筛选。
- `GET /api/v1/admin/mcp/logs/{id}`：查看单条调用元数据详情。
- `POST /api/v1/admin/mcp/logs/cleanup`：按当前保留期清理过期日志。
