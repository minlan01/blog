# 架构说明

## 总体架构

```
浏览器
  │
  ├─ 开发模式 ─── Vite Dev Server (:5173) ──proxy──▶ FastAPI (:8000)
  │
  └─ 生产模式 ─── Nginx (:80) ─────────────proxy──▶ FastAPI (:8000)
                    │
                    └── 静态文件 (Vue build 产物)
```

前后端完全分离，通过 REST API 通信。开发时 Vite 反向代理 `/api` 到后端；生产时 Nginx 承担相同角色。

## 前端架构

### 技术栈

- Vue 3 (Composition API + `<script setup>`)
- Vite 6 (构建 + HMR + 代理)
- TypeScript (严格模式)
- Vue Router 4 (History 模式)
- Pinia 3 (状态管理)
- Axios (HTTP 请求)
- markdown-it + highlight.js (Markdown 渲染 + 代码高亮)

### 目录结构

```
frontend/src/
├── api/                    # API 封装层
│   ├── http.ts             #   Axios 实例 + 拦截器 + safeCall 工具
│   ├── blog.ts             #   公开接口（文章/分类/标签/站点）
│   ├── auth.ts             #   认证接口（登录/注册/个人信息）
│   ├── comments.ts         #   评论接口
│   └── admin.ts            #   管理接口（CRUD）
├── assets/styles/          # 全局样式
│   ├── variables.css       #   设计令牌（颜色/字体/间距/圆角/阴影/过渡）
│   ├── base.css            #   Reset + 字体加载 + 页面过渡 + 滚动条
│   ├── code-highlight.css  #   Tokyo Night 代码高亮主题
│   └── main.css            #   导入入口（仅 3 行 @import）
├── components/             # 可复用组件
│   ├── blog/
│   │   └── PostCard.vue    #   文章卡片（封面 + meta + 标签 + hover 动效）
│   ├── common/
│   │   └── ErrorBanner.vue #   API 错误提示横幅（可重试）
│   ├── sidebar/            #   侧边栏组件
│   │   ├── ArchiveWidget.vue      #   文章归档（按月统计）
│   │   ├── CategoryWidget.vue     #   分类列表
│   │   ├── ProfileWidget.vue      #   个人资料卡片
│   │   ├── SiteStatsWidget.vue    #   站点统计（文章数/标签数/评论数）
│   │   └── TagCloudWidget.vue     #   标签云
│   └── landing/
│       └── OpeningScreen.vue  # 沉浸式全屏 Opening（光球/噪点/退场动画）
├── composables/            # 可复用逻辑
│   ├── useScrollReveal.ts  #   IntersectionObserver 滚动渐入
│   ├── useTheme.ts         #   主题切换（深色/浅色模式）
│   └── useImageUpload.ts   #   图片上传逻辑
├── layouts/
│   └── DefaultLayout.vue   #   主布局（Header + RouterView + Footer）
├── router/
│   └── index.ts            #   路由配置 + 滚动行为 + 动态标题
├── stores/
│   ├── site.ts             #   站点信息全局状态（含 error 状态 + 重试）
│   └── auth.ts             #   认证状态（用户信息 + token）
├── types/                  # TypeScript 类型
│   ├── blog.ts             #   业务类型（Post, Category, Tag, SiteProfile）
│   ├── auth.ts             #   认证类型（User, LoginRequest, RegisterRequest）
│   ├── comment.ts          #   评论类型
│   ├── highlight.d.ts      #   highlight.js 模块声明
│   └── markdown-it.d.ts    #   markdown-it 模块声明
├── utils/
│   └── markdown.ts         #   Markdown 渲染器（highlight.js 按需加载 8 种语言）
└── views/                  # 页面视图
    ├── HomeView.vue        #   首页（Opening → 精选 → 最近更新 → 分类）
    ├── PostsView.vue       #   文章列表（Immich 风格：侧边栏 + 图片网格）
    ├── PostDetailView.vue  #   文章详情（封面 + 进度条 + Markdown + 错误处理）
    ├── AboutView.vue       #   关于页（个人卡片 + 技术栈 + 滚动动画）
    ├── LoginView.vue       #   登录页
    ├── RegisterView.vue    #   注册页
    ├── ProfileView.vue     #   个人资料页
    ├── AdminView.vue       #   管理后台
    ├── CreatePostView.vue  #   创建文章页
    ├── EditPostView.vue    #   编辑文章页
    ├── SearchResultsView.vue  #  搜索结果页
    ├── CategoryPostsView.vue  #  分类文章列表页
    ├── ArchiveView.vue     #   归档页
    ├── FriendLinksView.vue #   友链页
    ├── MessageBoardView.vue #  留言板页
    ├── StatsView.vue       #   站点统计页
    └── NotFoundView.vue    #   404
```

### 数据流

```
页面挂载
  → onMounted / watch
    → api/blog.ts (或 stores/site.ts)
      → api/http.ts (axios 实例)
        → Vite proxy / Nginx
          → FastAPI
            → BlogService
              → SQLAlchemy → SQLite
```

认证流程：

```
用户登录
  → LoginView → api/auth.ts.login()
    → POST /api/v1/auth/login
      → 后端验证用户名密码
        → 生成 JWT token (有效期 7 天)
          → 前端存储 token (localStorage)
            → axios 拦截器自动添加 Authorization: Bearer {token}
              → 后端 JWT 验证 → CurrentUser 依赖注入
```

错误处理链路：

```
API 调用失败
  → axios 拦截器记录日志
  → safeCall() 返回 fallback 空值（非关键数据）
  → 或 try/catch 设置 errorMessage（关键数据如文章详情）
  → 页面显示 ErrorBanner 或错误状态 UI
  → 用户点击重试 → 重新加载
```

### 样式架构

项目使用 **CSS 变量 + scoped style** 方案：

- `variables.css`：全局设计令牌，所有组件通过 `var(--xxx)` 引用
- `base.css`：全局 reset、字体加载、页面过渡动画
- 各组件 `<style scoped>`：组件级样式，使用 BEM 命名（`block__element--modifier`）
- 不使用任何 CSS 框架，全部手写

### 关键设计决策

1. **Opening 用 fixed overlay 而非独立路由**：URL 始终是 `/`，退场动画更流畅
2. **PostsView 用前端筛选而非后端筛选**：数据量小时体验更好，切换瞬间响应
3. **markdown-it 按需注册 highlight.js 语言**：控制包体积，只注册 8 种常用语言
4. **safeCall 降级模式**：首页等聚合页面，部分 API 失败不影响其他内容展示

## 后端架构

### 技术栈

- Python 3.11+
- FastAPI (异步 web 框架)
- SQLAlchemy 2.x (ORM，声明式映射)
- Pydantic v2 (数据验证 + 序列化)
- SQLite (本地开发默认)

### 目录结构

```
backend/app/
├── api/v1/
│   ├── endpoints/          # 路由端点
│   │   ├── posts.py        #   GET /posts, GET /posts/{slug}
│   │   ├── categories.py   #   GET /categories
│   │   ├── tags.py         #   GET /tags
│   │   ├── site.py         #   GET /site/profile
│   │   ├── auth.py         #   POST /auth/login, /auth/register, /auth/profile
│   │   ├── comments.py     #   GET/POST/DELETE /comments
│   │   ├── messages.py     #   GET/POST /messages
│   │   ├── stats.py        #   GET /stats
│   │   ├── upload.py       #   POST /upload (需认证)
│   │   └── admin.py        #   POST/PUT/DELETE 管理接口
│   ├── api.py              #   路由聚合注册
│   └── deps.py             #   依赖注入（DBSession, CurrentUser, SuperAdmin）
├── core/
│   ├── config.py           #   Pydantic Settings 配置
│   └── security.py         #   JWT 工具（python-jose + bcrypt）
├── db/
│   ├── session.py          #   SQLAlchemy engine + session
│   ├── init_db.py          #   建表 + seed 入口
│   └── seed_data.py        #   示例数据（3 分类 + 8 标签 + 6 篇文章）
├── models/                 # 数据库模型
│   ├── post.py             #   Post + post_tags 关联表
│   ├── category.py         #   Category
│   ├── tag.py              #   Tag
│   ├── site_config.py      #   SiteConfig
│   ├── user.py             #   User (username, password_hash, role, bio, avatar)
│   ├── comment.py          #   Comment (content, post_id, user_id)
│   └── message.py          #   Message (name, email, content, color)
├── schemas/                # Pydantic 模型
│   ├── post.py             #   PostSummary / PostDetail / PostCreate / PostUpdate
│   ├── category.py         #   CategoryRead / CategoryCreate / CategoryUpdate
│   ├── tag.py              #   TagRead / TagCreate / TagUpdate
│   ├── site.py             #   SiteProfile / SiteProfileUpdate
│   ├── user.py             #   UserRead / UserCreate / UserLogin
│   ├── comment.py          #   CommentRead / CommentCreate
│   └── message.py          #   MessageRead / MessageCreate
├── services/
│   └── blog_service.py     #   业务逻辑（17 个方法）
└── main.py                 #   应用入口 + 中间件 + 异常处理
```

### 分层职责

| 层 | 职责 | 示例 |
|---|---|---|
| Endpoint | 接收请求、参数校验、返回响应 | `get_post(slug, db)` |
| Service | 业务逻辑、数据库操作 | `BlogService.get_post_by_slug(slug)` |
| Model | 数据库表结构定义 | `Post(title, slug, ...)` |
| Schema | 请求/响应数据格式 | `PostDetail(id, title, content_markdown)` |
| Security | JWT 认证、密码哈希 | `create_access_token(), verify_password()` |

### 认证与授权

- **JWT 认证**：使用 `python-jose` + `bcrypt`
  - 登录成功返回 access_token（有效期 7 天）
  - 前端在 Authorization header 携带：`Bearer {token}`
- **依赖注入**：
  - `CurrentUser`：从 token 解析当前用户（可能为 None）
  - `SuperAdmin`：验证用户为管理员（未登录返回 401）
- **密码安全**：
  - 注册/修改密码时使用 `bcrypt` 哈希（salt rounds=12）
  - 数据库不存储明文密码

### 数据模型

```
User ──1:N──▶ Comment ◀──N:1──▶ Post ◀──M:N──▶ Tag
                                       │
Category ──1:N──▶ Post                post_tags

Message (独立表)                SiteConfig (单例)
```

核心字段：

- **Post**: id, title, slug, summary, cover_image, content_markdown, reading_time, is_featured, published_at, category_id
- **Category**: id, name, slug, description
- **Tag**: id, name, slug
- **User**: id, username, password_hash, role (admin/user), bio, avatar, created_at
- **Comment**: id, content, post_id, user_id, created_at, parent_id (嵌套回复)
- **Message**: id, name, email, content, color, created_at, is_visible
- **SiteConfig**: site_name, hero_title, hero_subtitle, intro_text, avatar, email, github_url, location

## 部署架构

### 开发模式

```
Vite (:5173) ───proxy /api──▶ FastAPI (:8000) ──▶ SQLite (blog.db)
```

### Docker 生产模式

```
docker-compose.yml
├── frontend (Nginx :80)
│   ├── 静态文件 (/usr/share/nginx/html)
│   └── proxy /api → backend:8000
├── backend (Uvicorn :8000)
│   ├── SQLite (/app/data/blog.db)
│   └── uploads (/app/uploads)     # 用户上传文件
└── volumes:
    ├── blog-data (数据持久化)
    └── blog-uploads (上传文件持久化)
```

### 后续迁移路径

- SQLite → PostgreSQL：只需改 `DATABASE_URL` 环境变量 + 安装 psycopg2
- 本地文件 → OSS：图片上传接口改为写入 S3/MinIO
- 单机 → 集群：前端 build 放 CDN，后端用 Gunicorn 多 worker
- 新增功能：
  - 邮件通知（新评论/留言）
  - 文章全文搜索（Elasticsearch/Meilisearch）
  - CDN 加速（图片/静态资源）
  - 缓存层（Redis）
