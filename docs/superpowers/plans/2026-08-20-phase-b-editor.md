# B 阶段：文章编辑器与内容渲染一致性

## 状态

已实现并完成代码级验证。Compose/真实浏览器验收属于部署环境验证，不改变本阶段接口或数据结构。

## 范围

- Admin 桌面双栏 Markdown 编辑器，移动端编辑/预览 Tab。
- 标题、强调、链接、引用、列表、代码块、分隔线和图片上传工具栏。
- 预览支持 CommonMark、表格、脚注、代码高亮和 `$...$` / `$$...$$` 公式。
- draft 服务端自动保存：标题非空后创建 draft，后续按 2 秒防抖更新；已发布文章不自动保存。
- 自动保存状态、失败重试、路由离开保护和浏览器关闭保护。
- 后端输出统一 HTML 清洗，前台文章详情执行 Prism 与 KaTeX 增强渲染。

## 实现决策

- 编辑器仍使用 Element Plus `el-input` textarea，工具栏通过选区快照插入 Markdown，避免引入重量级编辑器和新的内容格式。
- Admin 预览使用 `markdown-it` + footnote/katex 插件 + DOMPurify；服务端存储使用 `markdown-it-py` + `dollarmath` + Bleach，统一保留 `language-*`、`data-tex`、`data-display` 语义。前台使用 SSR-safe `isomorphic-dompurify`，服务端和浏览器侧均执行同一危险 URL/HTML 清洗策略。
- 新文章只有标题非空才会在 2 秒防抖后创建 draft；创建成功后路由切换到 `/posts/{id}/edit`，内部切换不会触发离开确认。
- 自动保存请求通过 Promise 队列串行执行，失败保留内存内容并允许重试；已发布文章只显示显式保存提示。

## 接口与数据

- 复用 `POST /api/v1/admin/posts` 和 `PUT /api/v1/admin/posts/{id}`，不新增自动保存 API。
- 不新增数据库表或迁移，`PostCreate` / `PostUpdate` 请求字段保持不变。
- `content_html` 保留代码语言 class 和公式 `data-tex` / `data-display` 语义标记。
- HTML 清洗阻断脚本、事件属性和危险 URL，同时保留文章结构、链接、图片、脚注和公式标记。

## 验证

- `backend\\.venv\\Scripts\\python.exe -m pytest backend/tests -q`：29 passed。
- `backend\\.venv\\Scripts\\python.exe -m pytest backend/tests/test_markdown.py -q`：2 passed。
- `admin`: `npm run build` 通过（`vue-tsc -b` + Vite）。
- `frontend`: `npm run build` 通过（Nuxt client/server/Nitro）。
- 已核验公式、fenced code 语言 class、危险 HTML/URL 清洗和后端文章 CRUD 的 `content_md`/`content_html` 同步。
- 需要部署环境补做：桌面端、390px 移动端、暗色模式下的真实点击验收，以及 Compose 重建后的自动保存/离开保护交互回归。

## 留置范围

C 阶段继续处理复杂运营统计、全文搜索升级、协作编辑、版本历史和回滚。
