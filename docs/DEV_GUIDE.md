# 二次开发指南

这份文档帮助你理解项目的开发模式，快速上手扩展功能。

## 环境准备

### 系统要求

- Node.js 18+（推荐 20）
- Python 3.11+（推荐 3.12）
- npm 或 pnpm

### 首次安装

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 日常启动

```bash
# 终端 1
cd backend && source .venv/bin/activate && fastapi dev app/main.py

# 终端 2
cd frontend && npm run dev
```

后端 Swagger 文档：http://127.0.0.1:6965/docs

### 重置数据库

```bash
cd backend && rm -f blog.db && fastapi dev app/main.py
```

首次启动时 `init_db()` 会自动建表并写入 seed 数据。

---

## 如何添加新页面

以添加一个「归档页」为例：

### 1. 创建视图文件

```
frontend/src/views/ArchiveView.vue
```

```vue
<template>
  <section class="archive">
    <div class="container narrow-container">
      <header>
        <p class="archive__kicker">ARCHIVE</p>
        <h1>归档</h1>
      </header>
      <!-- 你的内容 -->
    </div>
  </section>
</template>

<script setup lang="ts">
// 导入需要的 API 和类型
import { onMounted, ref } from 'vue'
import { getPosts } from '@/api/blog'
import type { PostSummary } from '@/types/blog'

const posts = ref<PostSummary[]>([])
onMounted(async () => {
  posts.value = await getPosts()
})
</script>

<style scoped>
.archive {
  padding: var(--space-3xl) 0;
}
/* 使用 var(--xxx) 引用设计令牌 */
</style>
```

### 2. 注册路由

编辑 `frontend/src/router/index.ts`，在 `children` 数组中添加：

```ts
{
  path: 'archive',
  name: 'archive',
  component: () => import('@/views/ArchiveView.vue'),
  meta: { title: '归档' },
},
```

### 3. 添加导航链接

编辑 `frontend/src/layouts/DefaultLayout.vue`，在 `<nav>` 中添加：

```vue
<RouterLink to="/archive" class="shell__nav-link">归档</RouterLink>
```

---

## 如何添加新组件

### 组件位置规范

```
components/
├── blog/       # 博客业务组件（PostCard, CommentList 等）
├── common/     # 通用组件（ErrorBanner, Modal, Toast 等）
└── landing/    # 首页 Opening 相关组件
```

### 组件模板

```vue
<template>
  <div class="my-comp">
    <!-- 模板 -->
  </div>
</template>

<script setup lang="ts">
// 1. Props 用 interface 定义
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
})

// 2. Emits 用类型定义
const emit = defineEmits<{
  (e: 'click', id: number): void
}>()
</script>

<style scoped>
/* 使用 BEM 命名：block__element--modifier */
.my-comp { }
.my-comp__title { }
.my-comp__title--active { }
</style>
```

### 样式规范

- 始终使用 `<style scoped>`
- 颜色、间距、圆角等通过 `var(--xxx)` 引用 `variables.css` 中的令牌
- 过渡动画使用 `var(--duration-fast)` / `var(--ease-out)` 等预定义值
- 响应式断点：`640px`（手机）、`768px`（平板）、`920px`（小桌面）

---

## 如何添加新 API 接口

以添加「搜索文章」接口为例：

### 1. 后端：Schema

编辑 `backend/app/schemas/post.py`，添加搜索结果类型（如果和现有不同）。

### 2. 后端：Service

编辑 `backend/app/services/blog_service.py`：

```python
def search_posts(self, keyword: str) -> list[Post]:
    stmt = (
        select(Post)
        .options(joinedload(Post.category), joinedload(Post.tags))
        .where(Post.title.contains(keyword) | Post.summary.contains(keyword))
        .order_by(Post.published_at.desc())
    )
    return list(self.db.scalars(stmt).unique().all())
```

### 3. 后端：Endpoint

编辑 `backend/app/api/v1/endpoints/posts.py`：

```python
@router.get("/search", response_model=list[PostSummary])
def search_posts(db: DBSession, q: str = Query(..., min_length=1)):
    service = BlogService(db)
    return service.search_posts(q)
```

### 4. 前端：API 封装

编辑 `frontend/src/api/blog.ts`：

```ts
export async function searchPosts(keyword: string) {
  const { data } = await http.get<PostSummary[]>('/posts/search', {
    params: { q: keyword },
  })
  return data
}
```

### 5. 前端：在页面中使用

```ts
import { searchPosts } from '@/api/blog'

const results = ref<PostSummary[]>([])
async function onSearch(keyword: string) {
  results.value = await searchPosts(keyword)
}
```

---

## 如何添加新数据模型

以添加「评论」模型为例：

### 1. 创建 Model

```
backend/app/models/comment.py
```

```python
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
```

### 2. 注册 Model

编辑 `backend/app/models/__init__.py`：

```python
from app.models.comment import Comment
__all__ = [..., "Comment"]
```

在 `Post` model 中添加反向关系：

```python
comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
```

### 3. 创建 Schema

```
backend/app/schemas/comment.py
```

### 4. 扩展 Service + Endpoint

同上面 API 接口的模式。

### 5. 重置数据库

```bash
cd backend && rm -f blog.db && fastapi dev app/main.py
```

> 当前使用 SQLite + 自动建表模式。生产环境建议接入 Alembic 做数据迁移。

---

## 如何修改 Opening 首屏

Opening 组件位于 `frontend/src/components/landing/OpeningScreen.vue`。

### 结构说明

```
OpeningScreen
├── opening__bg          # 背景层
│   ├── opening__gradient    # 渐变底色 + 呼吸动画
│   ├── opening__orb--1/2/3  # 浮动光球（blur + 慢速漂移）
│   ├── opening__noise       # SVG 噪点纹理
│   └── opening__grid        # 点阵网格装饰
├── opening__content     # 内容层
│   ├── opening__kicker      # 顶部标签
│   ├── opening__title       # 主标题（渐变光效）
│   ├── opening__subtitle    # 副标题
│   └── opening__actions     # 按钮组
└── opening__footer      # 底部滚动提示
```

### 常见修改

**改标题文案**：编辑 `HomeView.vue` 中传给 OpeningScreen 的 props，或修改后端 `SiteConfig` seed 数据。

**改背景颜色**：修改 `opening__orb` 的 `background` 中的 rgba 颜色值。

**改动画速度**：调整各 `@keyframes` 的 `animation-duration`。

**添加新的视觉层**：在 `opening__bg` 内添加新的 div + 对应的 CSS 动画。

**改退场方式**：修改 `.opening-exit-leave-to` 的 transform 属性。

---

## 错误处理模式

### 非关键数据（首页、列表页）

使用 `safeCall` 降级：

```ts
import { safeCall } from '@/api/http'

const posts = await safeCall(() => getPosts(), [])
// 失败时 posts = []，页面仍可部分展示
```

### 关键数据（文章详情）

使用 try/catch + 错误状态：

```ts
try {
  post.value = await getPostBySlug(slug)
} catch (error) {
  if (axios.isAxiosError(error)) {
    errorMessage.value = error.response?.status === 404
      ? '文章不存在'
      : '接口请求失败'
  }
}
```

### 全局错误提示

使用 `ErrorBanner` 组件：

```vue
<ErrorBanner
  :visible="hasError"
  title="数据加载失败"
  description="请检查后端是否启动"
  @retry="loadData"
/>
```

---

## 设计令牌速查

所有令牌定义在 `frontend/src/assets/styles/variables.css`。

### 颜色

| 变量 | 用途 |
|---|---|
| `--color-bg-deep` | 最深背景 `#060a14` |
| `--color-bg` | 主背景 |
| `--color-surface` | 卡片/面板背景 |
| `--color-text` | 正文文字 |
| `--color-text-soft` | 次要文字 |
| `--color-text-muted` | 最弱文字 |
| `--color-accent` | 强调色（蓝） |
| `--color-accent-2` | 强调色（紫） |

### 间距

`--space-xs` (4px) → `--space-sm` (8) → `--space-md` (16) → `--space-lg` (24) → `--space-xl` (40) → `--space-2xl` (64) → `--space-3xl` (96)

### 动效

| 变量 | 值 | 用途 |
|---|---|---|
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | 标准缓出 |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | 弹性效果 |
| `--duration-fast` | `0.2s` | hover 等即时反馈 |
| `--duration-normal` | `0.4s` | 页面过渡 |
| `--duration-slow` | `0.7s` | Opening 等大型动画 |

---

## 构建与部署

### 前端构建

```bash
cd frontend && npm run build
```

产物在 `frontend/dist/`，可部署到任意静态托管（Nginx、Vercel、Netlify）。

### Docker 部署

```bash
docker compose up --build -d
```

### 环境变量

**后端** (`backend/.env`)：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `APP_NAME` | `Personal Blog API` | 应用名 |
| `API_V1_PREFIX` | `/api/v1` | API 路径前缀 |
| `CORS_ORIGINS` | `http://127.0.0.1:5173,...` | 允许的跨域来源 |
| `SQLITE_DB_PATH` | `blog.db` | 数据库文件路径 |

**前端** (`frontend/.env`)：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `VITE_API_BASE_URL` | `/api/v1` | API 基础路径 |
