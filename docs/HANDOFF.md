# 交给 AI 的开发接力说明

如果你要让 Claude 或其他 AI 继续开发这个项目，把这份文件连同代码一起提供。

## 项目当前状态

这是一个 **功能完整的全栈个人博客**，包含前后端完整实现、用户认证、内容管理和评论系统。

### 已完成

**前端功能：**
- Vue 3 + TypeScript 全栈实现
- Opening 首屏、文章列表（Immich 风格）、文章详情（代码高亮、复制按钮、图片灯箱）
- 关于页、搜索结果页、留言板页
- 管理后台：AdminView（仪表盘）、CreatePostView（新建文章）、EditPostView（编辑文章）
- 用户认证：登录、注册、个人中心页面
- 评论系统：CommentSection 组件，支持嵌套显示
- 主题切换：暗色/亮色模式，useTheme composable
- Markdown 增强：脚注支持、代码复制按钮、图片灯箱、共享编辑器样式

**后端功能：**
- FastAPI + SQLAlchemy，共 20+ 个端点
- 完整的用户认证：JWT（python-jose + bcrypt），登录/注册/个人资料 API
- 文章管理：公开 API + 管理 CRUD API
- 图片上传：`/api/v1/upload` 端点，基于 Bearer Token 认证
- 全文搜索：`/api/v1/search?q=keyword` 端点
- 评论系统：Comment 模型 + CRUD 端点
- 留言板：Message 模型 + 完整 API
- 统计 API：`/api/v1/stats` 返回真实数据库计数
- 管理端点：SuperAdmin 权限控制，基于 `deps.py` 依赖注入
- 全局错误处理、请求日志、CORS 配置

**基础设施：**
- Docker Compose 部署配置
- 环境变量管理（SECRET_KEY 从 .env 读取）
- 完整开发文档

### 未完成

- RSS Feed 生成
- SEO 优化（sitemap.xml、meta 标签、Open Graph）
- 数据库迁移（Alembic）
- 测试覆盖（pytest）
- CI/CD 流水线
- 国际化（i18n）
- 性能优化（懒加载、虚拟滚动）

## 技术栈（不要更换）

- frontend: Vue 3 + Vite + TypeScript + Vue Router + Pinia
- backend: FastAPI + SQLAlchemy + Pydantic + SQLite
- 样式: 纯 CSS（CSS 变量 + scoped style），无 Tailwind / UI 框架
- 认证: JWT (python-jose) + bcrypt

## 开发规范

### 前端

- 使用 `@/` 路径别名
- 组件用 `<script setup lang="ts">`
- 样式用 `<style scoped>` + BEM 命名
- 颜色/间距/动效通过 `var(--xxx)` 引用 `variables.css` 中的令牌
- API 调用统一封装在 `src/api/` 下
- 认证 token 存储在 localStorage，axios 拦截器自动添加 `Authorization: Bearer {token}`
- 非关键数据用 `safeCall()` 降级，关键数据用 try/catch + 错误状态

### 后端

- 四层分离：endpoint → service → model → schema
- Schema 区分 Read / Create / Update
- Service 方法返回 ORM 对象，由 endpoint 通过 response_model 序列化
- 新增端点放在对应的 endpoints 文件中，admin 操作放 admin.py
- 认证通过 `Authorization: Bearer {token}` header（不是 query parameter）
- 管理端点使用 `Depends(SuperAdmin)` 保护
- 时间统一使用 `datetime.now(timezone.utc)`，不再使用 `datetime.utcnow()`

### 文件组织

```
新页面    → src/views/XxxView.vue + 注册到 router
新组件    → src/components/{domain}/XxxYyy.vue
新 API    → 后端 endpoint + service + schema → 前端 src/api/
新数据模型 → 后端 model + schema → 删除 blog.db 重启
新样式    → 检查 variables.css 令牌，优先使用现有变量
```

## 架构变更说明

### 认证系统
- JWT Token 通过 `Authorization: Bearer` header 传递
- SECRET_KEY 从环境变量读取，不再硬编码
- 前端 axios 拦截器自动注入 token
- 登录/注册/个人资料 API 完整实现

### 权限控制
- 管理端点使用 `SuperAdmin` 依赖（`app/api/deps.py`）
- 图片上传端点需要认证
- 评论系统支持匿名和认证用户

### 数据模型
- User: username, hashed_password, is_admin
- Comment: 嵌套评论支持
- Message: 留言板独立模型
- Post/Category/Tag: 原有模型保持稳定

### 样式优化
- 编辑器样式提取到 `src/assets/editor.css`
- 代码块添加复制按钮
- 图片支持灯箱预览
- Markdown 脚注渲染

### 代码清理
- BlogService 重复方法已合并
- 统一使用 `datetime.now(timezone.utc)`
- 移除废弃的 query parameter 认证方式

## 最推荐的下一步任务

### 任务 1：RSS Feed 生成

1. 后端安装 `feedgen` 包
2. 新建 `app/api/v1/endpoints/feed.py`
3. 实现 `GET /api/v1/feed/rss` 和 `/api/v1/feed/atom`
4. 包含最新文章（标题、摘要、发布时间、作者）
5. 前端在 `<head>` 添加 `<link rel="alternate" type="application/rss+xml">`

### 任务 2：SEO 优化

1. **Sitemap**: `GET /sitemap.xml` 动态生成
2. **Meta 标签**: 文章详情页添加 description、keywords
3. **Open Graph**: 添加 og:title、og:description、og:image
4. **结构化数据**: 添加 JSON-LD schema
5. **robots.txt**: 静态文件

### 任务 3：友链后台管理

1. 扩展 `app/models/link.py`（FriendLink 模型）
2. 后端 CRUD 端点（`/api/v1/admin/links`）
3. 前端管理页面（`AdminLinksView.vue`）
4. 前台展示页面（`LinksView.vue`）

### 任务 4：真实分析集成

1. 集成 Umami 或 Plausible（隐私友好）
2. 在 Layout 中添加追踪脚本
3. 后端统计 API 增加访问量数据

### 任务 5：数据库迁移

1. 安装并初始化 Alembic
2. 生成初始迁移（`alembic revision --autogenerate -m "init"`）
3. 更新 `env.py` 使用 SQLAlchemy metadata
4. 文档化迁移流程

### 任务 6：测试覆盖

1. 安装 `pytest` + `httpx`
2. 后端 API 测试（tests/test_api/）
3. 前端组件测试（Vitest + Vue Test Utils）
4. 目标：关键路径 80% 覆盖率

### 任务 7：CI/CD 流水线

1. GitHub Actions 工作流
2. 后端：pytest + lint
3. 前端：type-check + unit tests
4. 自动部署到 VPS/Docker

## 注意事项

- 不要大规模推翻现有目录结构，做增量增强
- 每次修改保证项目可运行
- 如果需要改 `variables.css` 中的设计令牌，注意检查所有引用处
- 新增模型后使用 Alembic 迁移（或临时方案：删除 blog.db 重建）
- seed_data.py 中的文章内容可以随时替换成你自己的真实内容
- 认证相关的操作不要忘记添加 JWT token
- 管理端点必须使用 `SuperAdmin` 依赖保护
- 保持代码风格一致，遵循现有命名约定
