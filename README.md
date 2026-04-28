# Personal Blog — Vue 3 + FastAPI

一个前后端分离的个人博客系统，具备沉浸式 Opening 首页、文章管理、分类标签、代码高亮等能力。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Vue Router + Pinia + markdown-it-footnote |
| 后端 | Python + FastAPI + SQLAlchemy + Pydantic + bcrypt + python-jose |
| 数据库 | SQLite（本地开发） |
| 部署 | Docker Compose + Nginx |

## 项目结构

```
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/      # 路由端点（posts, categories, tags, site, admin, auth, comments, messages, stats）
│   │   │   └── deps.py         # 依赖注入（JWT 认证）
│   │   ├── core/               # 配置 + 安全（JWT, 密码哈希）
│   │   ├── db/                 # 数据库初始化 + seed
│   │   ├── models/             # SQLAlchemy 模型（User, Comment, Message, Stats）
│   │   ├── schemas/            # Pydantic 序列化
│   │   ├── services/           # 业务逻辑层
│   │   ├── utils/              # 工具函数（文件上传、搜索）
│   │   └── main.py             # 应用入口
│   ├── uploads/                # 图片上传目录
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 封装（blog + admin + auth）
│   │   ├── assets/
│   │   │   ├── styles/         # 设计令牌 + 全局样式 + 代码高亮 + 主题切换
│   │   │   └── images/         # 静态图片资源
│   │   ├── components/         # 组件（PostCard, OpeningScreen, ErrorBanner, TOC, CodeBlock, ImageLightbox）
│   │   ├── composables/        # 可复用逻辑（useScrollReveal, useTheme）
│   │   ├── layouts/            # 页面布局（含导航栏、页脚、主题切换）
│   │   ├── middleware/         # 路由守卫（认证检查）
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理（auth, theme）
│   │   ├── types/              # TypeScript 类型
│   │   ├── utils/              # 工具（Markdown 渲染器、日期格式化）
│   │   └── views/              # 页面视图（含管理后台、留言板、友链）
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md     # 架构说明（前后端 + 部署）
│   ├── DEV_GUIDE.md        # 二次开发指南（添加页面/组件/API/模型）
│   ├── API_REFERENCE.md    # 完整 API 接口文档
│   └── HANDOFF.md          # AI 接力开发说明
└── scripts/                    # 启动脚本（sh + ps1）
```

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
rm -f blog.db                   # 首次或需要重置数据时
fastapi dev app/main.py
```

- API: http://127.0.0.1:6965
- Swagger 文档: http://127.0.0.1:6965/docs
- 首次启动自动创建 SQLite 数据库并写入 seed 数据

### 前端

```bash
cd frontend
npm install
npm run dev
```

- Web: http://127.0.0.1:3710
- Vite proxy 自动将 `/api` 请求转发到后端 6965 端口

### 快捷启动

```bash
# Linux / macOS
bash scripts/start_backend.sh   # 终端 1
bash scripts/start_frontend.sh  # 终端 2

# Windows PowerShell
.\scripts\start_backend.ps1
.\scripts\start_frontend.ps1
```

## Docker 部署

```bash
docker compose up --build -d
```

- 前端: http://localhost（Nginx 代理，端口 80）
- 后端: http://localhost:6965
- 数据持久化在 Docker volume `blog-data` 中

## API 概览

### 公开接口 (Public)

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/site/profile` | 站点信息 |
| GET | `/api/v1/posts` | 文章列表（支持 `?search=关键词&page=1&per_page=10&featured=true&category=slug&tag=slug`） |
| GET | `/api/v1/posts/{slug}` | 文章详情 |
| GET | `/api/v1/categories` | 分类列表 |
| GET | `/api/v1/tags` | 标签列表 |
| GET | `/api/v1/comments?post_id=X` | 获取文章评论 |
| GET | `/api/v1/messages` | 留言板列表 |
| GET | `/api/v1/stats` | 站点统计数据 |
| GET | `/health` | 健康检查 |

### 认证接口 (Auth)

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/v1/auth/me` | 获取当前用户信息（需认证） |

### 管理接口 (Admin - 需认证)

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/upload` | 图片上传 |
| POST | `/api/v1/comments` | 创建评论 |
| POST | `/api/v1/messages` | 提交留言 |
| POST | `/api/v1/admin/posts` | 创建文章 |
| PUT | `/api/v1/admin/posts/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/posts/{id}` | 删除文章 |
| POST | `/api/v1/admin/categories` | 创建分类 |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类 |
| POST | `/api/v1/admin/tags` | 创建标签 |
| PUT | `/api/v1/admin/tags/{id}` | 更新标签 |
| DELETE | `/api/v1/admin/tags/{id}` | 删除标签 |
| PUT | `/api/v1/admin/site/profile` | 更新站点信息 |
| PUT | `/api/v1/admin/comments/{id}` | 审核评论 |
| DELETE | `/api/v1/admin/comments/{id}` | 删除评论 |
| DELETE | `/api/v1/admin/messages/{id}` | 删除留言 |

> 认证接口使用 JWT Token，在 Header 中携带：`Authorization: Bearer <token>`

## 已完成功能

### 核心功能
- [x] 沉浸式 Opening 首屏（光效、渐变、退场动画）
- [x] 博客首页（精选文章 + 最近更新 + 分类侧边栏）
- [x] Immich 风格文章列表（左侧导航 + 图片网格 + 日期分组）
- [x] 文章详情页（封面 banner + 代码高亮 + 阅读进度条 + 骨架屏）
- [x] 关于页（技术栈展示 + 滚动渐入动画）
- [x] 分类 / 标签筛选
- [x] 全局错误处理（API 拦截器 + ErrorBanner + 重试）
- [x] 后端请求日志 + 全局异常兜底
- [x] 管理后台 CRUD API（文章 / 分类 / 标签 / 站点）
- [x] Docker Compose 部署配置
- [x] 动态浏览器标题
- [x] 响应式布局（桌面 / 平板 / 手机）
- [x] TypeScript 全覆盖
- [x] 代码高亮（highlight.js Tokyo Night 主题）

### 用户系统
- [x] 用户认证（JWT / Session）
- [x] 用户注册 / 登录页面
- [x] 管理后台前端 UI（文章编辑器 + Markdown 编辑）
- [x] 受保护的路由（需要登录才能访问）

### 内容增强
- [x] 图片上传（本地存储）
- [x] 搜索功能（全文检索）
- [x] 评论系统（前端展示 + 后端管理）
- [x] 文章归档页（按年月分组）
- [x] Markdown 增强（目录导航 TOC、代码复制、图片灯箱、脚注）

### 用户体验
- [x] 暗色 / 亮色主题切换
- [x] 留言板（前后端完整）
- [x] 友链页面
- [x] 站点统计页面（基础数据展示）

## 下一阶段待办

### 优先级高
- [ ] RSS Feed 生成
- [ ] SEO（sitemap.xml、meta tags、Open Graph）

### 优先级中
- [ ] 友链后端管理（当前前端硬编码）
- [ ] 站点统计接入真实数据（Umami/Plausible）

### 优先级低
- [ ] Alembic 数据迁移
- [ ] pytest 测试覆盖
- [ ] CI/CD Pipeline
- [ ] 国际化 i18n
- [ ] 性能优化（图片懒加载、虚拟滚动）

## 开发文档

| 文档 | 内容 |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 前后端架构、目录结构、数据流、分层职责、部署架构 |
| [docs/DEV_GUIDE.md](docs/DEV_GUIDE.md) | 二次开发手册：如何添加页面、组件、API、数据模型、修改 Opening |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | 完整 API 接口文档（请求/响应示例、错误码） |
| [docs/HANDOFF.md](docs/HANDOFF.md) | AI 接力开发说明（给 Claude 或其他 AI 的上下文） |
