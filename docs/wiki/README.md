# YeYi 博客 Code Wiki

YeYi 博客是一个前后端分离的个人博客系统：**Nuxt 3 博客前台 + Vue 3 管理后台 + FastAPI 模块化单体后端 + MySQL/Redis**。视觉采用"洛克魔法书"设计风格（暖色羊皮纸 + 金色点缀 + 阿里妈妈方圆体）。

## 文档导航

| 文档 | 内容 |
|------|------|
| [01-架构总览](./01-架构总览.md) | 系统架构图、技术栈、三大子项目职责、模块间依赖关系 |
| [02-后端详解](./02-后端详解.md) | 后端入口/配置/数据库/公共依赖/中间件/工具，以及 6 大业务模块的模型、路由、服务详解 |
| [03-数据模型](./03-数据模型.md) | ER 关系图、全部表结构、数据迁移（Alembic） |
| [04-API参考](./04-API参考.md) | 全部 REST API 端点：认证、文章、分类、标签、评论、搜索、统计、站点配置、上传 |
| [05-前端详解](./05-前端详解.md) | 博客前台（Nuxt 3）与管理后台（Vue 3 + Element Plus）的页面、组件、状态管理与 API 层 |
| [06-部署与运维](./06-部署与运维.md) | 本地 Docker、生产 docker-compose、Nginx 网关、GitHub Actions CI/CD |
| [07-开发指南](./07-开发指南.md) | 本地开发环境搭建、运行、测试、代码约定与注意事项 |

## 项目一览

```
YeYi-boke/
├── frontend/           # 博客前台（Nuxt 3 SSR，面向访客，端口 3000）
├── admin/              # 管理后台（Vue 3 + Vite SPA，面向管理员，端口 3001）
├── backend/            # 后端 API（FastAPI 模块化单体，端口 8000）
│   └── app/modules/    # posts / comments / users / search / stats / config / mcp 管理模块
├── deploy/             # 生产部署配置（docker-compose.prod.yml、gateway.conf、.env.example）
├── docs/               # 设计文档与本 Wiki
├── gateway.conf        # 可选/历史网关配置；本地 Compose 不启用
├── docker-compose.yml  # 开发环境一键编排
└── .github/workflows/  # CI/CD（构建镜像推送阿里云 ACR + SSH 部署）
```

## 核心特性

- 混合内容博客（技术文章 + 生活随笔），Markdown 写作、服务端渲染 HTML
- 文章/分类/标签管理，slug 中文自动转拼音
- 访客评论系统（嵌套回复、审核流、站点配置开关）
- 全文搜索、RSS 订阅、访问统计（PV/UV 趋势）
- JWT 认证（access + refresh 双 token，refresh 存 Redis 可主动失效）
- 暗黑模式、KaTeX 数学公式、代码高亮
- Docker 一键部署，GitHub Actions 自动化发布
- MCP 独立管理服务：内容管理工具、API Key 管理、调用审计和后台可视化面板

## 快速开始

```bash
# Docker 本地直连启动（根目录，不启动 gateway/Nginx）
docker compose up -d --build

# 访问
# 博客前台  http://localhost:3000
# 管理后台  http://localhost:3001
# API      http://localhost:8000/docs
# MCP      http://localhost:8100/mcp
# 默认管理员 admin / admin123
```

> 生产环境才使用网关按域名分流；本地 Compose 直接暴露各服务端口。

详细本地开发步骤见 [07-开发指南](./07-开发指南.md)。
