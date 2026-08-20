# YeYi Blog MCP 可视化管理面板

## 当前状态

A 阶段“功能完整性 + 稳定性”已完成实现与验证。B 阶段“文章编辑器与内容渲染一致性”已完成代码实现和构建/测试验证，独立计划见 `docs/superpowers/plans/2026-08-20-phase-b-editor.md`；C 阶段运营分析暂不启动。

后端、admin 页面、MCP 多 Key 接入和本地 Compose 验证均已完成；生产部署前仍需核验公网证书。前台已完成 Firefly 信息架构参考下的三栏布局、墨色纸张色阶、公开统计与独立头像配置；两端构建、Compose 重建及本地截图复核均已完成。

### 已完成

- 新增 `backend/app/modules/mcp/` 管理域：MCP 设置、请求日志模型、schema、service、admin router。
- 新增 Alembic migrations：`7f4f8d1c2a11_add_mcp_management.py`、`a4b6c8d0e2f1_add_mcp_api_keys.py`；当前 head 为 `a4b6c8d0e2f1`。
- FastAPI 已注册 MCP 管理接口：
  - `GET /api/v1/admin/mcp/overview`
  - `GET/PUT /api/v1/admin/mcp/settings`
  - `GET/POST /api/v1/admin/mcp/keys`
  - `PATCH/DELETE /api/v1/admin/mcp/keys/{key_id}`
  - `GET /api/v1/admin/mcp/keys/{key_id}/export-url`
  - `GET /api/v1/admin/mcp/logs`
  - `GET /api/v1/admin/mcp/logs/{log_id}`
  - `POST /api/v1/admin/mcp/logs/cleanup`
- MCP API Key 支持 Fernet 加密保存；`mcp_api_keys` 支持多个独立 Key 的添加、启停、删除、使用次数统计和 Redis 即时失效。
- MCP 鉴权中间件已改为数据库/Redis 设置优先，支持启停、限流、Host/Origin、真实客户端 IP（`X-Real-IP`）。
- MCP 工具审计已接入独立事务日志，记录工具名、请求 ID、IP、耗时、结果、资源 ID/slug 及 Key ID/名称/指纹；不记录正文、评论内容、Base64 或密钥。
- admin 已新增 `admin/src/api/mcp.ts`、`admin/src/views/MCPManagement.vue`、`/mcp` 路由和左侧“MCP 管理”菜单项。
- Compose 已向 backend 和 mcp 注入 MCP 设置环境变量。
- MCP 专项测试与管理测试通过：`9 passed`；全量后端测试通过：`18 passed`。
- Python compileall、开发/生产 Compose config 已通过。
- 启动本地 MySQL 8.0 与 Redis 7 后，MCP 专项管理测试通过：`8 passed`；全量 REST 测试通过：`17 passed`。
- `admin` 的 `npm ci` 与 `npm run build` 已通过；`frontend` 的 `npm ci` 与 Nuxt `npm run build` 已通过；`MCPManagement.vue` 无 Vue/Element Plus 类型错误。
- Alembic 已在 MySQL 应用至 `a4b6c8d0e2f1`，`mcp_service_settings`、`mcp_api_keys`、`mcp_request_logs` 及相关索引已核验。
- 真实 backend/mcp/Redis/MySQL 端到端验证已完成：`?tavilyApiKey=<key>` 接入成功，停用/错误 Key 为 `401`；Key 使用次数和工具审计日志可展示客户端 IP、工具名、结果、耗时、资源 slug 及 Key 名称。
- 部署 Wiki、`.env.example` 与 CI 已更新为 MCP bootstrap、Fernet 密钥、后台轮换和日志保留策略。
- 前台 `>=1280px` 使用 224px 左栏 + 中央内容 + 224px 右栏，低于该宽度隐藏侧栏并恢复单列阅读；左右栏采用 sticky widget 分组。
- 新增公开 `GET /api/v1/stats/summary`，只返回今日 PV、已发布文章、分类、标签和已通过评论的聚合数量。
- 站点配置新增 `avatar_url`，后台站点配置支持上传或填写 URL；前台头像为空时使用站点标题首字符 fallback。
- 文章目录仅收集 H2/H3，H3 缩进显示，H4 排除；无目录时右栏回退到最新文章和统计。
- 前台正文浅色主题已调整为近纯黑墨色（正文 `#17130F`、标题 `#0B0907`），公告入口统一支持完整版浮现弹窗，页面切换使用 220ms 浮现过渡并兼容 reduced-motion。
- RSS 后端接口已修复无时区发布时间导致的 feedgen 500，公开 `GET /api/v1/rss.xml` 可正常返回 XML；按当前产品决定，RSS 图标已从桌面与移动端导航隐藏，接口保留供后续启用。
- 暗色主题已修复正文不可见问题：`typography.css` 的正文、标题、列表、表格和引用改用主题 token，暗色正文/标题/次级文字分别提升为 `#F4EEE1`、`#FFF8E8`、`#E0D1BC`；同时增强暗色边框和 caption 对比度。
- A 阶段已修复前台首页分类/标签筛选，并让分页保留筛选条件；归档页改为每页 50 篇分页加载，避免超过 API 上限后丢失文章。
- A 阶段已补齐前台评论关闭状态、回复入口、父评论归属校验，以及按 `comment_need_review` 展示发布/待审核反馈。
- A 阶段已补齐 admin 文章状态筛选、分类/标签编辑删除与排序、站点公告/社交链接编辑、Logo 展示、评论文章上下文和标题过滤。
- A 阶段已接入 admin 401 队列式静默刷新；refresh token 增加唯一 `jti`，确保同一秒刷新也会轮换；登录、评论、搜索、上传分别接入 Redis 限流。
- A 阶段验证结果：后端全量测试 `27 passed`；admin `npm run build` 通过；frontend `npm run build` 通过。
- A 阶段已同步更新 `docs/wiki/01-架构总览.md` 与 `docs/wiki/02-后端详解.md`，移除限流未挂载和静默刷新未实现的过时描述。
- B 阶段已完成 Admin 双栏 Markdown 编辑器、移动端编辑/预览 Tab、工具栏选区操作、draft 自动保存队列、失败重试和离开保护。
- B 阶段已完成后端 Markdown 清洗、代码语言 class、`$...$`/`$$...$$` 公式语义标记，以及前台 Prism/KaTeX 增强渲染；未新增文章 CRUD 接口、数据库表或迁移。
- B 阶段验证结果：后端全量 `29 passed`；Markdown 专项 `2 passed`；admin 和 frontend 构建均通过。真实浏览器交互和 Compose 重建保留为部署验收项。

### 当前阻塞/未完成

- MCP 生产网关与 CI 注入已补齐：`deploy/gateway.conf` 新增 `blogmcp.yeyeyiyi.online` 的 80/443、`/mcp` 和 `/health` 路由；部署流水线现在要求 `MCP_API_KEY`、`MCP_SETTINGS_ENCRYPTION_KEY` secrets，并写入 Host/Origin 限制；生产 Compose 对这两个变量启用必填校验。服务器证书目录 `/etc/liteSSL/YeYi-blog` 仍需确认存在 `blogmcp` 与 `blogmcp-key` 且 SAN 包含该域名。
- 首次部署后仍需从 admin `/mcp` 的“密钥管理”创建独立 Key，并按需停用 bootstrap Key。

## 继续执行顺序

1. 已完成：启动 MySQL/Redis 或使用可用测试数据库，运行：
   - `backend\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_mcp.py backend/tests/test_mcp_admin.py -q`
   - `backend\\.venv\\Scripts\\python.exe -m pytest backend/tests -q`
2. 已完成：运行 Alembic：`cd backend; alembic upgrade head`，确认 `mcp_service_settings`、`mcp_api_keys` 与 `mcp_request_logs` 表和索引存在。
3. 已完成：在 `admin` 执行 `npm ci` 和 `npm run build`，验证 `MCPManagement.vue` 的 Element Plus/Vue 类型。
4. 已完成：登录 admin 创建独立 API Key，验证 `tavilyApiKey` 查询参数接入、Key 使用计数和停用后 `401`。
5. 已完成：调用 MCP 工具后，在 admin 的“请求日志”验证 IP、工具名、耗时、结果、资源标识。
6. 已完成：更新部署 Wiki 的密钥轮换、migration、日志保留和面板地址说明。
7. 已完成：压暗 `frontend/assets/css/main.css` 与 `admin/src/style.css` 的浅色变量，提升文字、边框及 Element Plus 控件对比度；前台头部、页脚和主内容统一到更紧凑的 `max-w-5xl` 容器。
8. 已完成：收敛 admin Dashboard/MCP 卡片圆角和阴影，优化布局滚动与窄屏标题；MCP 筛选控件在移动端全宽排列，宽表格和分页提供横向滚动承载。
9. 已完成：`admin`、`frontend` 的 `npm run build` 均通过，后端全量测试为 `20 passed`，`docker compose up -d --build` 已重建并启动全部服务；在 `http://localhost:3000`、`http://localhost:3001` 和已认证的 `http://localhost:3001/mcp` 完成桌面与 390px 窄屏检查。页面没有空白渲染、元素重叠或根页面横向溢出；MCP 宽表格在窄屏由独立滚动容器承载。截图存于 `docs/evaluations/ui-check-20260819/`。
10. 已完成：A 阶段测试先在本地 MySQL 未启动时记录 setup 阻塞，启动 Compose MySQL/Redis 后完成 RED/GREEN 验证；最终后端全量为 `27 passed`，两端构建均通过。

## 关键设计约定

- 使用现有 `admin` 角色，不新增 superadmin。
- API Key 明文只在创建 Key 的 POST 请求中传输，不在响应、数据库、日志或浏览器持久化。
- `MCP_SETTINGS_ENCRYPTION_KEY` 是运行必需的加密材料，由 Compose 提供稳定默认值，不能在后台页面修改。
- `MCP_API_KEY` 只负责首次创建设置记录时的 bootstrap；后台“密钥管理”保存的多个 Key 以数据库加密值为准。
- 默认日志保留 90 天；日志清理支持后台手动触发，并由写日志流程通过 Redis 锁周期触发。
- MCP 工具正常返回不因审计日志写入失败而失败。
- 普通 admin API 的 access token 失效时，客户端先使用 refresh token 静默刷新并重放一次请求；refresh 失败才清除登录态。
- 限流默认按 `X-Real-IP`、`X-Forwarded-For` 首个地址或请求客户端地址识别 IP；登录 10/分钟、评论 5/分钟、搜索 30/分钟、上传 50/小时。
- B 阶段自动保存只处理 draft；published 文章不会后台自动 PUT，必须显式点击保存更新。
- B 阶段不引入 C 阶段的复杂运营统计、全文搜索升级、协作编辑、版本历史和回滚。
