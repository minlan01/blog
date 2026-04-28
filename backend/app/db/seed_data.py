from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Category, Comment, FriendLink, Post, SiteConfig, Tag, User


def _seed_users(db: Session) -> None:
    # Migrate old admin user to minlan01 if it exists
    old_admin = db.scalar(select(User).where(User.username == "admin"))
    if old_admin:
        old_admin.username = "minlan01"
        old_admin.role = "super_admin"
        old_admin.password_hash = hash_password("minlan01")
        old_admin.bio = "Super Administrator"
        db.commit()
        return

    # Create minlan01 if no users exist
    existing = db.scalar(select(User).where(User.username == "minlan01"))
    if not existing:
        admin_user = User(
            username="minlan01",
            password_hash=hash_password("minlan01"),
            role="super_admin",
            bio="Super Administrator",
        )
        db.add(admin_user)
        db.commit()


def seed_database(db: Session) -> None:
    if db.query(SiteConfig).first():
        # Site already seeded; just seed users if missing
        if not db.query(User).first():
            _seed_users(db)
        return

    # ── 分类 ──
    engineering = Category(name="工程", slug="engineering", description="架构、开发与重构")
    design_cat = Category(name="设计", slug="design", description="视觉、交互与体验")
    life = Category(name="随笔", slug="essays", description="个人表达与记录")

    # ── 标签 ──
    vue_tag = Tag(name="Vue3", slug="vue3")
    fastapi_tag = Tag(name="FastAPI", slug="fastapi")
    design_tag = Tag(name="Design", slug="design")
    writing_tag = Tag(name="Writing", slug="writing")
    ts_tag = Tag(name="TypeScript", slug="typescript")
    css_tag = Tag(name="CSS", slug="css")
    python_tag = Tag(name="Python", slug="python")
    devops_tag = Tag(name="DevOps", slug="devops")

    db.add_all([
        engineering, design_cat, life,
        vue_tag, fastapi_tag, design_tag, writing_tag,
        ts_tag, css_tag, python_tag, devops_tag,
    ])
    db.flush()

    # ── 站点配置 ──
    site = SiteConfig(
        site_name="minlan01",
        hero_title="SYSTEM ONLINE\nACCESS GRANTED",
        hero_subtitle="// Terminal blog system ready.",
        intro_text="Engineer, design enthusiast. Building with code, recording thoughts with words.",
        avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=400&auto=format&fit=crop",
        email="hello@example.com",
        github_url="https://github.com/minlan01",
        location="Taipei",
        icp_filing="",
        icp_link="",
    )

    # ── 文章 ──
    posts = [
        Post(
            title="为什么这个博客要重构成前后端分离",
            slug="why-rebuild-to-decoupled-architecture",
            summary="从默认初始化模板，过渡到一个可持续开发、可本地部署的博客工程骨架。选择 FastAPI 而不是 Django 或 Flask，核心考虑是类型系统和 Pydantic 的结合，让 API 层几乎不需要额外的文档维护成本。",
            cover_image="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=1200&auto=format&fit=crop",
            reading_time="6 min",
            is_featured=True,
            published_at=datetime(2026, 4, 10, 10, 0),
            category=engineering,
            tags=[vue_tag, fastapi_tag],
            content_markdown=_MD_DECOUPLED,
        ),
        Post(
            title="Opening 首屏质感",
            slug="how-to-design-a-better-opening-screen",
            summary="好的 opening 不是单纯的大图和按钮。",
            cover_image="https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=1200&auto=format&fit=crop",
            reading_time="5 min",
            is_featured=True,
            published_at=datetime(2026, 4, 8, 20, 30),
            category=design_cat,
            tags=[design_tag, css_tag],
            content_markdown=_MD_OPENING,
        ),
        Post(
            title="如何把这个框架继续做成真正可用的个人博客",
            slug="roadmap-for-a-real-usable-personal-blog",
            summary="从框架骨架到可上线博客，中间还需要补齐内容管理、SEO、搜索、评论和部署能力。每个阶段完成后都应该保证项目可运行、可演示。推荐开发顺序：视觉还原、内容管理、体验增强、工程化。",
            cover_image="https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop",
            reading_time="7 min",
            is_featured=False,
            published_at=datetime(2026, 4, 6, 19, 0),
            category=engineering,
            tags=[fastapi_tag, devops_tag],
            content_markdown=_MD_ROADMAP,
        ),
        Post(
            title="TypeScript 在 Vue 3 项目中的最佳实践",
            slug="typescript-best-practices-in-vue3",
            summary="类型不是负担，而是让代码自我解释的方式。",
            cover_image="https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop",
            reading_time="8 min",
            is_featured=True,
            published_at=datetime(2026, 4, 12, 14, 0),
            category=engineering,
            tags=[ts_tag, vue_tag],
            content_markdown=_MD_TYPESCRIPT,
        ),
        Post(
            title="CSS 变量系统：从混乱到秩序",
            slug="css-variables-from-chaos-to-order",
            summary="一套好的 CSS 变量系统可以让整个项目的视觉语言保持一致，同时让主题切换变得轻松。变量命名应该描述用途而非值，例如 --color-accent 而不是 --green。",
            cover_image="https://images.unsplash.com/photo-1507721999472-8ed4421c4af2?q=80&w=1200&auto=format&fit=crop",
            reading_time="5 min",
            is_featured=False,
            published_at=datetime(2026, 4, 4, 11, 0),
            category=design_cat,
            tags=[css_tag, design_tag],
            content_markdown=_MD_CSS_VARS,
        ),
        Post(
            title="写作是最被低估的工程师技能",
            slug="writing-is-underrated-engineering-skill",
            summary="代码的读者不只有编译器，还有六个月后的自己和整个团队。写作能力决定了你的影响半径。写 RFC、写设计文档的过程，会迫使你把模糊的直觉变成清晰的逻辑。",
            cover_image="https://images.unsplash.com/photo-1455390582262-044cdead277a?q=80&w=1200&auto=format&fit=crop",
            reading_time="4 min",
            is_featured=False,
            published_at=datetime(2026, 4, 2, 9, 30),
            category=life,
            tags=[writing_tag],
            content_markdown=_MD_WRITING,
        ),
    ]

    db.add(site)
    db.add_all(posts)
    db.flush()

    # ── 用户：minlan01 作为 super_admin ──
    admin_user = User(
        username="minlan01",
        password_hash=hash_password("minlan01"),
        role="super_admin",
        bio="Super Administrator",
    )
    test_user = User(
        username="reader",
        password_hash=hash_password("reader123"),
        role="user",
        bio="热爱阅读的旅行者",
    )
    db.add_all([admin_user, test_user])
    db.flush()

    # ── 评论 ──
    comments = [
        Comment(content="写得很清晰，对前后端分离的理解更深了！", post_id=posts[0].id, user_id=test_user.id),
        Comment(content="期待后续关于部署的分享。", post_id=posts[0].id, user_id=admin_user.id),
        Comment(content="Opening 设计的层次分析很有启发。", post_id=posts[1].id, user_id=test_user.id),
    ]
    db.add_all(comments)

    # ── Friend Links ──
    if not db.query(FriendLink).first():
        friend_links = [
            FriendLink(name="安知鱼", url="https://blog.mcxiaochen.top/", avatar="https://bu.dusays.com/2023/04/09/64329399db87e.png", description="种一棵树最好的时间是十年前，其次是现在。", category="推荐博客", badge="主题开发者", sort_order=1),
            FriendLink(name="张洪Heo", url="https://blog.zhheo.com/", description="分享设计与科技生活", category="推荐博客", sort_order=2),
            FriendLink(name="Leonus", url="https://blog.leonus.top/", description="一蓑烟雨任平生", category="推荐博客", sort_order=3),
            FriendLink(name="Vercel", url="https://vercel.com", description="前端部署平台", category="推荐服务商", badge="部署", sort_order=1),
            FriendLink(name="Cloudflare", url="https://cloudflare.com", description="CDN 与安全服务", category="推荐服务商", sort_order=2),
            FriendLink(name="GitHub", url="https://github.com", description="代码托管平台", category="推荐服务商", badge="开源", sort_order=3),
        ]
        db.add_all(friend_links)

    db.commit()


# ────────────────────────────────
#  Markdown 内容（保持 seed_database 函数简洁）
# ────────────────────────────────

_MD_DECOUPLED = """\
## 为什么要拆分

当一个个人博客要继续做成视觉型首页 opening、文章内容系统、后台管理和 SEO 部署，前后端分离会更稳。

> 好的架构不是一开始就完美的，而是让后续改进变得容易。

## 现在这个骨架解决了什么

1. 前端已经切换成 **Vue 3 + TypeScript**，使用 Vite 构建。
2. 后端已经提供文章、分类、标签、站点信息接口。
3. 本地开发可以直接使用 SQLite，零配置。
4. 后续只需要在这个结构上增量开发。

## 技术选型的考量

选择 FastAPI 而不是 Django 或 Flask，核心考虑是：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/posts")
async def list_posts():
    # 自动生成 OpenAPI 文档
    # 自动请求验证
    # 原生 async 支持
    return {"posts": []}
```

FastAPI 的类型系统和 Pydantic 的结合，让 API 层几乎不需要额外的文档维护成本。

## 接下来最值得做的事

- 还原 opening 风格，让首屏有仪式感
- 增加文章管理后台，支持在线编辑
- 增强 Markdown 展示效果，包括代码高亮和目录导航
- 接入 Docker 部署脚本，一键上线
"""

_MD_OPENING = """\
## Opening 的三个层次

一个好的 opening 首屏，是背景层、内容层、转场层三者协同的结果。

### 1. 背景层

背景不是装饰，是氛围的基础。几种常见的处理方式：

- **渐变叠加**：多层径向渐变 + 线性渐变，营造深度感
- **光球浮动**：用 `filter: blur()` 和 CSS 动画模拟柔和光效
- **噪点纹理**：SVG feTurbulence 生成的微妙噪点，增加质感
- **点阵网格**：用 `background-image: radial-gradient()` 做 subtle 网格

```css
.orb {
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(80px);
  background: radial-gradient(
    circle,
    rgba(122, 162, 247, 0.2),
    transparent 70%
  );
  animation: float 12s ease-in-out infinite alternate;
}
```

### 2. 内容层

内容层的关键是**克制**——不是信息越多越好，而是每个元素都有存在的理由。

- 一个足够有力的主标题
- 一行简短的副标题
- 一个明确的行动按钮

### 3. 转场层

用户从 opening 进入正文的那一刻，是体验的关键拐点。好的转场应该是**无缝的**，让用户感觉是"被邀请进入"而不是"被强制切换"。

## 工程建议

先保证结构成立，再慢慢逼近视觉参考。不要在第一个版本就追求完美动效。
"""

_MD_ROADMAP = """\
## 推荐开发顺序

从一个框架骨架到可上线的博客，建议按以下顺序推进：

### 第一阶段：视觉还原
- 首页 opening 动效
- 文章卡片交互
- 详情页排版

### 第二阶段：内容管理
- 后台管理界面
- 文章 CRUD
- 图片上传

### 第三阶段：体验增强
- Markdown 扩展（代码高亮、目录导航、图片灯箱）
- 搜索功能
- 评论系统

### 第四阶段：工程化
- Alembic 数据迁移
- pytest 测试覆盖
- Docker Compose 部署

```python
# 未来的后台逻辑示例
from fastapi import APIRouter

admin_router = APIRouter(prefix="/admin")

@admin_router.post("/posts")
async def create_post(title: str, content: str):
    # TODO: 实现文章创建
    return {"status": "created"}
```

每个阶段完成后都应该保证项目可运行、可演示。
"""

_MD_TYPESCRIPT = """\
## 为什么 TypeScript 很重要

在 Vue 3 项目中使用 TypeScript 不是为了炫技，而是为了：

- **自我文档化**：类型即文档，读代码时不需要猜测数据结构
- **重构安全**：改一个接口字段，编译器会告诉你所有需要同步修改的地方
- **更好的 IDE 支持**：自动补全、跳转定义、参数提示

## Props 类型定义

```typescript
// 用 interface 定义 Props，比 runtime 声明更精确
interface PostCardProps {
  post: PostSummary
  showCover?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<PostCardProps>(), {
  showCover: true,
  compact: false,
})
```

## Pinia Store 的类型推断

```typescript
export const useSiteStore = defineStore('site', () => {
  // ref<T> 自动推断，不需要额外声明
  const profile = ref<SiteProfile | null>(null)
  const loading = ref(false)

  async function loadProfile() {
    if (profile.value) return
    loading.value = true
    try {
      profile.value = await getSiteProfile()
    } finally {
      loading.value = false
    }
  }

  return { profile, loading, loadProfile }
})
```

## API 层的类型安全

```typescript
// 泛型让返回值自动推断
export async function getPosts(
  params?: { featured?: boolean }
) {
  const { data } = await http.get<PostSummary[]>(
    '/posts', { params }
  )
  return data  // 类型自动推断为 PostSummary[]
}
```

关键原则：**让类型为你工作，而不是让你为类型工作。**
"""

_MD_CSS_VARS = """\
## 问题：样式值到处散落

在没有设计系统的项目里，你会看到 `#333`、`#666`、`rgba(0,0,0,0.5)` 散落在几十个文件中。改一个颜色意味着全局搜索替换。

## 解决方案：CSS 变量系统

```css
:root {
  /* 色彩 */
  --color-bg: #0a0a0a;
  --color-text: #b0ffb0;
  --color-accent: #00ff41;

  /* 间距 */
  --space-md: 16px;
  --space-lg: 24px;

  /* 圆角 */
  --radius-md: 6px;

  /* 过渡 */
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## 命名原则

变量命名应该描述**用途**而非**值**：

- `--color-accent` 而不是 `--green`
- `--space-lg` 而不是 `--24px`
- `--radius-card` 而不是 `--rounded-lg`

## 暗色/亮色主题切换

有了变量系统，主题切换只需要覆盖变量值：

```css
[data-theme="light"] {
  --color-bg: #f0f0f0;
  --color-text: #1a1a1a;
  --color-accent: #006600;
}
```

整个页面的颜色会自动跟随变化，不需要改任何组件代码。
"""

_MD_WRITING = """\
## 代码和文章的共同点

两者都是在向读者传递信息。区别只在于：

- 代码的读者是**编译器 + 人**
- 文章的读者是**纯粹的人**

但在实际工作中，代码的"人类读者"比编译器重要得多。六个月后的你、新加入团队的同事、Code Review 的同事——他们都需要读懂你的代码。

> 好的代码和好的文章一样，应该让读者感觉"这很自然"。

## 写作如何帮助工程师

### 1. 理清思路

写 RFC、写设计文档的过程，会迫使你把模糊的直觉变成清晰的逻辑。很多架构问题在"写下来"的那一刻就自然暴露了。

### 2. 扩大影响力

一个好的技术分享帖、一篇清晰的故障复盘，能让你的影响力超越代码本身。

### 3. 异步沟通

远程团队的核心能力就是**异步沟通**，而异步沟通的载体就是文字。写得清楚，别人就不需要拉会议来"对齐"。

## 建议

每周写一篇短文，题目不限。可以是技术总结、工具分享、工作反思。重要的是**持续输出**，而不是追求完美。
"""
