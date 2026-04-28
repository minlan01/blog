# API 接口文档

基础路径：`/api/v1`

完整的交互式文档可在后端启动后访问：http://127.0.0.1:6965/docs

---

## 认证方式

所有需要认证的接口使用 JWT Bearer Token：

```
Authorization: Bearer {access_token}
```

获取 token 方式见「认证接口」部分。

---

## 公开接口

### GET /site/profile

获取站点配置信息。

**响应示例：**

```json
{
  "site_name": "Lan Min",
  "hero_title": "把表达、设计与工程\n折叠进同一个入口",
  "hero_subtitle": "A cinematic personal blog...",
  "intro_text": "工程师、设计爱好者...",
  "avatar": "https://...",
  "email": "hello@example.com",
  "github_url": "https://github.com/yourname",
  "location": "Taipei"
}
```

### GET /posts

获取文章列表（分页）。

**查询参数：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `featured` | `bool` | 只返回精选文章 |
| `category` | `string` | 按分类 slug 筛选 |
| `tag` | `string` | 按标签 slug 筛选 |
| `search` | `string` | 搜索关键词 |
| `page` | `int` | 页码（默认 1） |
| `per_page` | `int` | 每页数量（默认 10） |

**响应示例：**

```json
{
  "items": [
    {
      "id": 1,
      "title": "文章标题",
      "slug": "post-slug",
      "summary": "文章摘要",
      "cover_image": "https://...",
      "reading_time": "6 min",
      "published_at": "2026-04-10T10:00:00",
      "is_featured": true,
      "category": { "id": 1, "name": "工程", "slug": "engineering", "description": "..." },
      "tags": [
        { "id": 1, "name": "Vue3", "slug": "vue3" }
      ]
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3
}
```

### GET /posts/{slug}

获取单篇文章详情（含 Markdown 正文）。

**路径参数：** `slug` — 文章的 URL 友好标识

**响应：** 同文章列表项，额外包含 `content_markdown` 字段。

**错误：** `404` — 文章不存在

### GET /categories

获取所有分类。

**响应示例：**

```json
[
  { "id": 1, "name": "工程", "slug": "engineering", "description": "架构、开发与重构" },
  { "id": 2, "name": "设计", "slug": "design", "description": "视觉、交互与体验" }
]
```

### GET /tags

获取所有标签。

**响应示例：**

```json
[
  { "id": 1, "name": "Vue3", "slug": "vue3" },
  { "id": 2, "name": "FastAPI", "slug": "fastapi" }
]
```

### GET /stats

获取站点统计数据。

**响应示例：**

```json
{
  "posts": 25,
  "categories": 4,
  "tags": 18,
  "comments": 42,
  "users": 3,
  "messages": 7
}
```

### GET /messages

获取所有留言。

**响应示例：**

```json
[
  {
    "id": 1,
    "name": "访客",
    "email": "visitor@example.com",
    "content": "留言内容",
    "created_at": "2026-04-10T10:00:00"
  }
]
```

### POST /messages

创建新留言。

**请求体：**

```json
{
  "name": "访客姓名",
  "email": "visitor@example.com",
  "content": "留言内容"
}
```

**必填字段：** `name`, `content`
**可选字段：** `email`

**响应：** `201` + 创建的 Message 对象

### GET /comments?post_id=X

获取指定文章的评论。

**查询参数：** `post_id` — 文章 ID

**响应示例：**

```json
[
  {
    "id": 1,
    "content": "评论内容",
    "created_at": "2026-04-10T10:00:00",
    "author": {
      "id": 1,
      "username": "user1"
    }
  }
]
```

### GET /health

健康检查。

**响应：** `{ "status": "ok" }`

---

## 认证接口

### POST /auth/register

注册新用户。

**请求体：**

```json
{
  "username": "newuser",
  "password": "securepassword123"
}
```

**必填字段：** `username` (3-20字符), `password` (6字符以上)

**响应示例：**

```json
{
  "id": 1,
  "username": "newuser",
  "bio": null,
  "avatar": null,
  "is_admin": false,
  "created_at": "2026-04-10T10:00:00"
}
```

**错误：** `400` — 用户名已存在或验证失败

### POST /auth/login

用户登录。

**请求体：**

```json
{
  "username": "user1",
  "password": "password123"
}
```

**响应示例：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**错误：** `401` — 用户名或密码错误

### GET /auth/me

获取当前用户信息。

**请求头：** `Authorization: Bearer {token}`

**响应示例：**

```json
{
  "id": 1,
  "username": "user1",
  "bio": "这是我的个人简介",
  "avatar": "https://...",
  "is_admin": true,
  "created_at": "2026-04-10T10:00:00"
}
```

**错误：** `401` — 未提供 token 或 token 无效

### PUT /auth/me

更新当前用户信息。

**请求头：** `Authorization: Bearer {token}`

**请求体（局部更新）：**

```json
{
  "bio": "更新后的个人简介",
  "avatar": "https://new-avatar-url"
}
```

**可选字段：** `bio`, `avatar`

**响应：** `200` + 更新后的 UserRead 对象

---

## 管理接口（需要 super_admin 权限）

> 以下接口需要超级管理员 JWT token，在请求头中携带：`Authorization: Bearer {admin_token}`

### POST /admin/posts

创建文章。

**请求体：**

```json
{
  "title": "新文章标题",
  "slug": "new-post-slug",
  "summary": "文章摘要",
  "content_markdown": "## Hello\n\n正文内容...",
  "cover_image": "https://...",
  "reading_time": "5 min",
  "is_featured": false,
  "category_id": 1,
  "tag_ids": [1, 3]
}
```

**必填字段：** `title`, `slug`, `summary`, `content_markdown`

**响应：** `201` + 完整的 PostDetail 对象

**错误：** `409` — slug 已存在

### PUT /admin/posts/{id}

更新文章（局部更新，只传需要修改的字段）。

**请求体示例：**

```json
{
  "title": "更新后的标题",
  "is_featured": true
}
```

**响应：** `200` + 更新后的 PostDetail

**错误：** `404` — 文章不存在，`409` — slug 冲突

### DELETE /admin/posts/{id}

删除文章。

**响应：** `204` 无内容

**错误：** `404` — 文章不存在

### POST /admin/categories

创建分类。

**请求体：**

```json
{
  "name": "新分类",
  "slug": "new-category",
  "description": "分类描述"
}
```

### PUT /admin/categories/{id}

更新分类。

**请求体（局部）：**

```json
{
  "name": "更新后的分类名",
  "description": "新描述"
}
```

### DELETE /admin/categories/{id}

删除分类。

### POST /admin/tags

创建标签。

**请求体：**

```json
{
  "name": "NewTag",
  "slug": "newtag"
}
```

### PUT /admin/tags/{id}

更新标签。

**请求体（局部）：**

```json
{
  "name": "UpdatedTag"
}
```

### DELETE /admin/tags/{id}

删除标签。

### PUT /admin/site/profile

更新站点配置（局部更新）。

**请求体示例：**

```json
{
  "site_name": "新站名",
  "hero_title": "新标题"
}
```

### POST /upload

上传文件（图片等）。

**请求类型：** `multipart/form-data`

**请求体：** 文件字段名为 `file`

**响应示例：**

```json
{
  "url": "https://example.com/uploads/image-123.jpg",
  "filename": "image-123.jpg"
}
```

---

## 评论接口（需要认证）

### POST /comments

创建评论。

**请求头：** `Authorization: Bearer {token}`

**请求体：**

```json
{
  "content": "这是我的评论",
  "post_id": 1
}
```

**必填字段：** `content`, `post_id`

**响应示例：**

```json
{
  "id": 1,
  "content": "这是我的评论",
  "created_at": "2026-04-10T10:00:00",
  "post_id": 1,
  "author": {
    "id": 1,
    "username": "user1"
  }
}
```

**错误：** `404` — 文章不存在，`401` — 未登录

### DELETE /comments/{id}

删除评论（仅评论作者或管理员可操作）。

**请求头：** `Authorization: Bearer {token}`

**响应：** `204` 无内容

**错误：** `403` — 无权限，`404` — 评论不存在

---

## 统一响应格式

### 成功

- 列表接口：直接返回数组 `[...]` 或分页对象 `{items: [...], total, page, per_page, total_pages}`
- 详情接口：直接返回对象 `{...}`
- 创建接口：`201` + 创建后的对象
- 更新接口：`200` + 更新后的对象
- 删除接口：`204` 无内容

### 错误

所有错误返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

状态码含义：

| 状态码 | 含义 |
|---|---|
| `400` | 请求参数验证失败 |
| `401` | 未认证或 token 无效 |
| `403` | 权限不足 |
| `404` | 资源不存在 |
| `409` | 资源冲突（如 slug 重复） |
| `422` | 请求体格式错误（Pydantic 验证） |
| `500` | 服务器内部错误 |

---

## 前端 API 封装

所有接口已在前端封装好，可直接导入使用：

```ts
// 公开接口
import {
  getSiteProfile,
  getPosts,
  getPostBySlug,
  getCategories,
  getTags,
  getStats,
  getMessages,
  createMessage,
  getComments
} from '@/api/blog'

// 认证接口
import {
  register,
  login,
  getCurrentUser,
  updateCurrentUser
} from '@/api/auth'

// 管理接口
import {
  createPost,
  updatePost,
  deletePost
} from '@/api/admin/posts'
import {
  createCategory,
  updateCategory,
  deleteCategory
} from '@/api/admin/categories'
import {
  createTag,
  updateTag,
  deleteTag
} from '@/api/admin/tags'
import {
  updateSiteProfile
} from '@/api/admin/site'
import {
  uploadFile
} from '@/api/admin/upload'

// 评论接口
import {
  createComment,
  deleteComment
} from '@/api/comments'
```
