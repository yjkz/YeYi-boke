# YeYi 博客系统设计文档

> 日期：2026-06-23
> 状态：待审阅

---

## 1. 项目概述

YeYi 博客是一个个人博客系统，采用前后端分离架构，前端使用 Nuxt 3 (Vue 3 + SSR)，后端使用 FastAPI (Python)，数据存储使用 MySQL + Redis。视觉风格参考洛克魔法书设计系统（暖色羊皮纸 + 金色点缀 + 圆体字体），并根据博客场景灵活调整。

### 1.1 核心特性

- 混合内容博客（技术文章 + 生活随笔）
- Markdown + HTML 写作
- 暗黑模式
- 代码高亮
- 数学公式渲染 (KaTeX)
- RSS 订阅
- 全文搜索
- 访客评论系统
- 管理员后台
- 访问统计

---

## 2. 系统架构

### 2.1 当前阶段：模块化单体

先用单体 FastAPI 跑通所有功能，但代码按业务域模块化组织。后期拆微服务时，直接把模块文件夹独立出去即可。

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────────────┐
│   博客前端       │     │   管理后台       │     │   FastAPI 后端（模块化单体）      │
│   (Nuxt 3)      │────▶│   (Vue 3)       │────▶│                                 │
│   Port: 3000    │     │   Port: 3001    │     │  ┌────────┐ ┌────────┐          │
└─────────────────┘     └─────────────────┘     │  │ posts  │ │comments│  ...     │
                                                 │  │ module │ │ module │          │
                                                 │  └────────┘ └────────┘          │
                                                 └──────────────┬──────────────────┘
                                                                │
                                                      ┌─────────┴─────────┐
                                                      │                   │
                                                 ┌────▼────┐        ┌────▼────┐
                                                 │  MySQL  │        │  Redis  │
                                                 │  3306   │        │  6379   │
                                                 └─────────┘        └─────────┘
```

### 2.2 未来阶段：微服务拆分

当需要练手微服务时，按以下边界拆分：

```
┌──────────────┐
│ API Gateway  │  (Nginx / Kong / Traefik)
│  Port: 8000  │
└──┬───┬───┬───┘
   │   │   │
   ▼   ▼   ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│posts │ │comms │ │users │ │search│ │stats │ │config│
│:8001 │ │:8002 │ │:8003 │ │:8004 │ │:8005 │ │:8006 │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   │        │        │        │        │        │
   └────────┴────────┴────┬───┴────────┴────────┘
                          │
                    ┌─────┴─────┐
                    │           │
               ┌────▼────┐ ┌───▼────┐
               │  MySQL  │ │ Redis  │
               └─────────┘ └────────┘
```

**微服务拆分清单（6 个服务）：**

| 服务 | 职责 | 端口 |
|------|------|------|
| posts-service | 文章 CRUD、分类、标签 | 8001 |
| comments-service | 评论、审核 | 8002 |
| users-service | 认证、用户管理 | 8003 |
| search-service | 全文搜索 | 8004 |
| stats-service | 访问统计、分析 | 8005 |
| config-service | 站点配置、公告 | 8006 |

**拆分策略：** 每个模块从一开始就是独立的文件夹，有自己的 router / service / model / schema。拆分时只需：
1. 把文件夹复制为独立项目
2. 添加独立的 main.py 和数据库连接
3. 在 Gateway 注册路由

### 2.3 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 博客前端 | Nuxt 3 (Vue 3) | SSR，面向访客 |
| 管理后台 | Vue 3 (独立项目) | SPA，面向管理员 |
| 后端 API | FastAPI (Python) | 模块化单体 → 微服务 |
| 数据库 | MySQL 8.0+ | 主数据存储 |
| 缓存 | Redis 7+ | 会话、缓存、限流 |
| 部署 | 自建服务器 | Nginx 反向代理 |

### 2.4 项目结构

```
YeYi boke/
├── frontend/              # 博客前端 (Nuxt 3)
├── admin/                 # 管理后台 (Vue 3)
├── backend/               # 后端 API (FastAPI 模块化单体)
│   ├── app/
│   │   ├── main.py        # FastAPI 应用入口
│   │   ├── config.py      # 全局配置
│   │   ├── database.py    # 数据库连接
│   │   ├── dependencies.py # 公共依赖（认证、分页等）
│   │   ├── modules/       # ★ 业务模块（每个模块 = 未来的一个微服务）
│   │   │   ├── posts/     # 文章模块
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── model.py
│   │   │   │   ├── schema.py
│   │   │   │   └── __init__.py
│   │   │   ├── comments/  # 评论模块
│   │   │   ├── users/     # 用户认证模块
│   │   │   ├── search/    # 搜索模块
│   │   │   ├── stats/     # 统计模块
│   │   │   └── config/    # 站点配置模块
│   │   ├── middleware/    # 中间件（CORS、限流、访问日志）
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试
│   ├── alembic/           # 数据库迁移
│   ├── uploads/           # 上传文件存储
│   ├── requirements.txt
│   └── alembic.ini
├── docs/                  # 文档
└── docker-compose.yml     # 用户自行编写（参考设计文档第9章）
```

**模块内部结构（以 posts 为例）：**

```
modules/posts/
├── __init__.py        # 模块注册，导出 router
├── router.py          # API 路由定义（FastAPI Router）
├── service.py         # 业务逻辑层
├── model.py           # SQLAlchemy 数据模型
├── schema.py          # Pydantic 请求/响应模型
├── repository.py      # 数据访问层（可选，复杂查询时抽取）
└── constants.py       # 模块内常量（可选）
```

**模块间通信规则：**
- 当前阶段（单体）：模块间直接 import 调用
- 拆分后（微服务）：通过 HTTP API 或消息队列调用
- 约定：模块间只通过 service 层调用，不直接访问其他模块的 model/repository

---

## 3. 数据模型

### 3.1 用户表 (users)

管理员账号，仅用于后台登录。

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    avatar VARCHAR(500),
    role ENUM('admin', 'editor') DEFAULT 'admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 文章表 (posts)

```sql
CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content_md LONGTEXT,          -- Markdown 原文
    content_html LONGTEXT,        -- 渲染后的 HTML
    excerpt VARCHAR(500),         -- 摘要
    cover_image VARCHAR(500),     -- 封面图 URL
    status ENUM('draft', 'published') DEFAULT 'draft',
    category_id INT,
    view_count INT DEFAULT 0,
    is_top BOOLEAN DEFAULT FALSE, -- 置顶
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
```

### 3.3 分类表 (categories)

```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 标签表 (tags)

```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 文章标签关联表 (post_tags)

```sql
CREATE TABLE post_tags (
    post_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### 3.6 评论表 (comments)

```sql
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL,
    parent_id INT,                -- 回复的评论 ID，NULL 表示顶级评论
    nickname VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    website VARCHAR(200),
    content TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    visitor_ip VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);
```

### 3.7 站点配置表 (site_config)

```sql
CREATE TABLE site_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(50) UNIQUE NOT NULL,
    config_value TEXT,
    description VARCHAR(200),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

预置配置项：

| config_key | 说明 | 示例值 |
|------------|------|--------|
| site_title | 站点标题 | YeYi 的博客 |
| site_subtitle | 副标题 | 记录生活与代码 |
| logo_url | Logo 图片 | /images/logo.png |
| favicon_url | Favicon | /favicon.ico |
| announcement | 公告内容 | 欢迎来到我的博客！ |
| footer_text | 页脚文字 | © 2026 YeYi |
| social_links | 社交链接 JSON | {"github":"...","twitter":"..."} |
| comment_enabled | 是否开启评论 | true |
| comment_need_review | 评论是否需要审核 | true |

### 3.8 访问记录表 (visit_logs)

```sql
CREATE TABLE visit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    page_path VARCHAR(500) NOT NULL,
    page_title VARCHAR(200),
    visitor_ip VARCHAR(45),
    user_agent VARCHAR(500),
    referer VARCHAR(500),
    country VARCHAR(50),
    city VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_page_path (page_path(100))
);
```

### 3.9 访问统计表 (visit_stats)

```sql
CREATE TABLE visit_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stat_date DATE UNIQUE NOT NULL,
    page_views INT DEFAULT 0,
    unique_visitors INT DEFAULT 0,
    top_pages JSON,  -- [{"path":"/posts/xxx","title":"...","views":123}]
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 4. API 设计

### 4.1 公开 API（博客前端）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/search?q=xxx` | 搜索文章 |
| GET | `/api/v1/posts` | 文章列表（分页、筛选） |
| GET | `/api/v1/posts/{slug}` | 文章详情 |
| GET | `/api/v1/categories` | 分类列表 |
| GET | `/api/v1/tags` | 标签列表 |
| POST | `/api/v1/comments` | 提交评论 |
| GET | `/api/v1/site/config` | 站点配置 |
| GET | `/api/v1/site/announcement` | 公告 |
| POST | `/api/v1/visit` | 记录访问 |

### 4.2 管理 API（管理后台，需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 管理员登录 |
| POST | `/api/v1/auth/logout` | 登出 |
| GET | `/api/v1/admin/posts` | 文章列表（含草稿） |
| POST | `/api/v1/admin/posts` | 创建文章 |
| PUT | `/api/v1/admin/posts/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/posts/{id}` | 删除文章 |
| POST | `/api/v1/admin/posts/{id}/publish` | 发布（草稿→发布） |
| POST | `/api/v1/admin/posts/{id}/draft` | 下架（发布→草稿） |
| POST | `/api/v1/admin/upload` | 上传图片 |
| GET | `/api/v1/admin/comments` | 评论管理 |
| PUT | `/api/v1/admin/comments/{id}` | 审核评论 |
| DELETE | `/api/v1/admin/comments/{id}` | 删除评论 |
| CRUD | `/api/v1/admin/categories` | 分类管理 |
| CRUD | `/api/v1/admin/tags` | 标签管理 |
| PUT | `/api/v1/admin/site/config` | 更新站点配置 |
| GET | `/api/v1/admin/stats` | 概览（今日PV、总文章数、总评论数） |
| GET | `/api/v1/admin/stats/trend` | 趋势（7天/30天PV曲线） |

### 4.3 认证方式

使用 JWT (JSON Web Token)：
- 登录后返回 access_token + refresh_token
- access_token 有效期 2 小时，通过 Authorization: Bearer header 传递
- refresh_token 有效期 7 天，存储在 Redis 中
- 管理 API 通过中间件校验 token

### 4.4 API → 模块映射

| 模块 | 拆分后服务 | 负责的 API |
|------|-----------|-----------|
| posts | posts-service (8001) | `/api/v1/posts/*`, `/api/v1/categories/*`, `/api/v1/tags/*`, `/api/v1/archive` |
| comments | comments-service (8002) | `/api/v1/comments/*`, `/api/v1/admin/comments/*` |
| users | users-service (8003) | `/api/v1/auth/*`, `/api/v1/admin/upload` |
| search | search-service (8004) | `/api/v1/search` |
| stats | stats-service (8005) | `/api/v1/visit`, `/api/v1/admin/stats/*`, `/api/v1/admin/analytics` |
| config | config-service (8006) | `/api/v1/site/config`, `/api/v1/site/announcement`, `/api/v1/admin/site/config` |

### 4.5 限流策略

使用 Redis 实现：
- 评论接口：同一 IP 每分钟最多 5 次
- 搜索接口：同一 IP 每分钟最多 30 次
- 登录接口：同一 IP 每分钟最多 10 次
- 上传接口：已登录用户每小时最多 50 次

---

## 5. 页面设计

### 5.1 博客前端页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 文章列表 + 站点公告 |
| 文章详情 | `/posts/{slug}` | 文章内容 + 评论区 |
| 分类 | `/categories` | 分类列表 + 文章数 |
| 标签 | `/tags` | 标签云 |
| 归档 | `/archive` | 按时间线归档 |
| 搜索 | `/search?q=xxx` | 搜索结果 |
| 关于 | `/about` | 关于页面 |
| RSS | `/rss.xml` | RSS 订阅 |

### 5.2 管理后台页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录 | `/login` | 管理员登录 |
| 仪表盘 | `/admin` | 访问统计概览 |
| 文章管理 | `/admin/posts` | 文章列表、新建、编辑 |
| 评论管理 | `/admin/comments` | 评论审核、删除 |
| 分类管理 | `/admin/categories` | 分类 CRUD |
| 标签管理 | `/admin/tags` | 标签 CRUD |
| 站点配置 | `/admin/settings` | 站点标题、Logo、公告等 |
| 访问统计 | `/admin/analytics` | 访问量、热门页面 |

---

## 6. 视觉设计

### 6.1 设计风格

参考洛克魔法书设计系统（Rocom Grimoire），根据博客场景灵活调整：

- 暖色羊皮纸背景
- 金色主色强调
- 圆体字体（Alimama FangYuanTi）
- 纸张质感的卡片和阴影
- 暗黑模式（暖棕色基调）

### 6.2 博客场景调整

**与 Rocom 原版的区别：**

- 文章正文区域使用更舒适的行高（1.8）和更大的字号（18px），优化长文阅读体验
- 代码块使用深色背景 + 语法高亮（Prism.js / Shiki），与羊皮纸风格形成对比但保持协调
- 目录导航（TOC）使用书签风格的侧边栏设计
- 评论区使用信纸/卷轴的视觉隐喻
- 管理后台减少装饰性元素，突出功能性，保留金色强调色

### 6.3 关键页面视觉

**首页：**
- 羊皮纸质感的文章卡片网格
- 金色分类标签，圆角胶囊形
- 悬浮阴影效果（暖棕色阴影）
- 顶部公告栏，卷轴样式

**文章详情：**
- 居中阅读区域（max-width: 720px）
- 左侧 TOC 目录（大屏时固定，小屏时折叠）
- 代码块深色背景 + 语法高亮
- 数学公式 KaTeX 渲染
- 底部评论区，信纸风格

**分类/标签：**
- 金色标签云，圆角胶囊形
- 分类卡片带文章计数

**管理后台：**
- 简洁的暖色调表单和表格
- 金色强调按钮和激活态
- 侧边栏导航

### 6.4 配色方案

沿用 Rocom 设计系统的配色，核心色值：

| Token | 色值 | 用途 |
|-------|------|------|
| `--rocom-bg` | `#FFF6E0` | 页面主背景 |
| `--rocom-bg-paper` | `#F4ECDC` | 纸张/卡片背景 |
| `--rocom-text` | `#3D3528` | 主文字 |
| `--rocom-primary` | `#F5BC00` | 主色（金色） |
| `--rocom-accent-orange` | `#D57F24` | 橙色点缀 |
| `--rocom-accent-blue` | `#2F6FDA` | 蓝色点缀 |

暗色模式：

| Token | 色值 | 用途 |
|-------|------|------|
| `--rocom-bg` | `#17120F` | 页面主背景 |
| `--rocom-bg-paper` | `#2A241E` | 纸张背景 |
| `--rocom-text` | `#F4EEE1` | 主文字 |
| `--rocom-primary` | `#FFD460` | 主色（金色，更亮） |

### 6.5 字体

```css
--font-brand: "Alimama FangYuanTi", "Microsoft YaHei", "PingFang SC", sans-serif;
--font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
```

### 6.6 代码高亮

代码块配色方案（深色背景，与羊皮纸风格协调）：

- 背景色：`#2D2A24`（暖棕深色）
- 文字色：`#F4EEE1`（暖白）
- 关键字：`#FFD460`（金色）
- 字符串：`#86EFAC`（柔和绿）
- 注释：`#918A7C`（暖灰）
- 函数名：`#93C5FD`（柔和蓝）

---

## 7. 功能详细设计

### 7.1 Markdown 渲染

使用 markdown-it + 插件：
- markdown-it-anchor：标题锚点
- markdown-it-toc：目录生成
- markdown-it-katex：数学公式
- markdown-it-prism：代码高亮
- markdown-it-image-lazyload：图片懒加载

文章创建/更新时：
1. 接收 Markdown 原文
2. 渲染为 HTML 并存储到 content_html
3. 生成摘要（取前 200 字或手动设置）

### 7.2 搜索功能

MySQL 全文搜索：
- 使用 MySQL FULLTEXT INDEX
- 搜索字段：title, content_md, excerpt
- 支持中文分词（ngram parser）
- 结果按相关性排序

### 7.3 评论系统

- 访客填写昵称、邮箱（可选）、网站（可选）、评论内容
- 支持嵌套回复（parent_id）
- 评论默认需要管理员审核（可配置）
- 使用 Akismet 或关键词过滤垃圾评论
- 限流：同一 IP 每分钟最多 5 条

### 7.4 访问统计

- 前端每次页面加载时调用 POST /api/v1/visit
- 记录：页面路径、IP、User-Agent、Referer
- 后台定时任务（每天凌晨）聚合统计到 visit_stats 表
- 仪表盘展示：今日 PV、总文章数、总评论数、7天/30天趋势图

### 7.5 RSS 订阅

使用 Python 的 feedgen 库生成 RSS 2.0 / Atom 格式：
- 包含最近 20 篇已发布文章
- 每篇文章包含标题、摘要、链接、发布时间

### 7.6 图片上传

- 管理后台支持上传封面图和文章内图片
- 图片存储在服务器本地（uploads/ 目录）
- 通过 Nginx 静态文件服务
- 支持图片压缩和缩略图生成

---

## 8. 安全设计

### 8.1 认证与授权

- JWT 认证，access_token 短有效期（2小时）
- refresh_token 存储在 Redis，支持主动失效
- 密码使用 bcrypt 哈希
- 管理 API 统一中间件校验

### 8.2 输入验证

- 所有 API 输入使用 Pydantic 模型校验
- 评论内容过滤 XSS（HTML 转义）
- SQL 注入防护（使用 SQLAlchemy ORM）

### 8.3 限流与防刷

- Redis 实现接口限流
- 评论防刷（IP + 内容相似度检测）
- 登录失败次数限制（5次后锁定15分钟）

### 8.4 CORS 配置

- 仅允许前端域名和管理后台域名访问 API
- 生产环境通过 Nginx 统一代理，避免 CORS 问题

---

## 9. 部署方案

> **注意：本章节仅作为参考文档，不纳入实现计划。部署由用户自行练习完成。**

### 9.1 Nginx 配置

```nginx
# 博客前端
server {
    listen 80;
    server_name blog.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;  # Nuxt SSR
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /uploads/ {
        alias /var/www/yeyi/uploads/;
        expires 30d;
    }
}

# 管理后台
server {
    listen 80;
    server_name admin.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:3001;  # Vue SPA
    }
}

# API 后端
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;  # FastAPI
    }
}
```

### 9.2 Docker Compose（当前：模块化单体）

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: yeyi_blog
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    environment:
      DATABASE_URL: mysql+asyncmy://root:${MYSQL_ROOT_PASSWORD}@mysql:3306/yeyi_blog
      REDIS_URL: redis://redis:6379/0

volumes:
  mysql_data:
```

### 9.3 Docker Compose（未来：微服务拆分后）

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine

  gateway:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./nginx/gateway.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - posts-service
      - comments-service
      - users-service
      - search-service
      - stats-service
      - config-service

  posts-service:
    build: ./services/posts-service
    expose:
      - "8001"
    environment:
      SERVICE_PORT: 8001

  comments-service:
    build: ./services/comments-service
    expose:
      - "8002"
    environment:
      SERVICE_PORT: 8002

  users-service:
    build: ./services/users-service
    expose:
      - "8003"
    environment:
      SERVICE_PORT: 8003

  search-service:
    build: ./services/search-service
    expose:
      - "8004"
    environment:
      SERVICE_PORT: 8004

  stats-service:
    build: ./services/stats-service
    expose:
      - "8005"
    environment:
      SERVICE_PORT: 8005

  config-service:
    build: ./services/config-service
    expose:
      - "8006"
    environment:
      SERVICE_PORT: 8006

volumes:
  mysql_data:
```

---

## 10. 开发计划概要

### 阶段一：模块化单体（先跑通）

1. **后端 API** — FastAPI 项目搭建、模块化目录结构、数据模型、全部 API 实现
2. **博客前端** — Nuxt 3 项目搭建、页面开发、Rocom 风格集成
3. **管理后台** — Vue 3 项目搭建、管理页面开发
4. **联调测试** — 前后端联调、功能测试
5. **~~部署上线~~** — 用户自行完成（Docker / Nginx / 服务器）

### 阶段二：微服务拆分（练手）

1. **拆分 users-service** — 最小依赖，先练手拆分流程
2. **拆分 comments-service** — 依赖 posts，练习服务间调用
3. **拆分 search-service** — 独立搜索，练习数据同步
4. **拆分 stats-service** — 独立统计，练习异步数据处理
5. **拆分 posts-service / config-service** — 完成全部拆分
6. **API Gateway** — Nginx/Kong 统一路由
7. **服务注册与发现** — Consul 或 Nacos（可选）

---

## 附录：依赖清单

### 后端 (Python)
- fastapi
- uvicorn
- sqlalchemy[asyncio]
- asyncmy (MySQL async driver)
- redis
- python-jose (JWT)
- passlib[bcrypt]
- python-multipart (file upload)
- feedgen (RSS)
- pydantic

### 博客前端 (Nuxt 3)
- nuxt 3
- @nuxtjs/color-mode (暗黑模式)
- @vueuse/core
- markdown-it + 插件
- katex
- prismjs / shiki

### 管理后台 (Vue 3)
- vue 3
- vue-router
- pinia
- axios
- element-plus 或 naive-ui
- @vueup/vue-quill (富文本编辑器)
