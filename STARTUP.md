# 个人博客 - 启动指南

## 项目结构

```
blog/
├── frontend/          # Vue 3 前端
├── backend/           # FastAPI 后端
├── scripts/           # 一键启动脚本
└── docker-compose.yml # Docker 部署
```

## 环境要求

- **Node.js** >= 18
- **Python** >= 3.11
- **Git**

---

## 快速启动（本地开发）

### 第一步：启动后端

打开一个终端：

```powershell
cd F:\blog\backend

# 首次运行：创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 后续启动：激活虚拟环境后直接运行
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 6965
```

后端启动成功后会显示：
- API 地址：http://127.0.0.1:6965
- API 文档：http://127.0.0.1:6965/docs

> 首次启动会自动创建 `blog.db`（SQLite）并插入种子数据，包括管理员账号。

### 第二步：启动前端

打开**另一个**终端：

```powershell
cd F:\blog\frontend

# 首次运行：安装依赖
npm install

# 后续启动：直接运行
npm run dev
```

前端启动成功后访问：http://localhost:3710

> 前端已配置代理，`/api` 请求自动转发到后端 `127.0.0.1:6965`。

---

## 账号信息

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 (super_admin) | minlan01 | minlan01 |
| 普通用户 | reader | reader123 |

---

## 页面路由

| 路径 | 页面 | 需要登录 | 需要管理员 |
|------|------|----------|------------|
| `/` | 首页（开幕 + 精选文章） | - | - |
| `/posts` | 文章列表 | - | - |
| `/posts/:slug` | 文章详情 | - | - |
| `/about` | 关于页面 | - | - |
| `/search` | 搜索结果 | - | - |
| `/category/:slug` | 分类文章 | - | - |
| `/login` | 登录 | - | - |
| `/register` | 注册 | - | - |
| `/profile` | 个人资料 | 是 | - |
| `/admin` | 后台管理 | 是 | 是 |
| `/create-post` | 写文章 | 是 | 是 |
| `/edit-post/:slug` | 编辑文章 | 是 | 是 |

---

## 常用命令

### 前端

```powershell
cd F:\blog\frontend

npm run dev        # 开发服务器（热更新）
npm run build      # 生产构建（输出到 dist/）
npm run preview    # 预览生产构建
```

### 后端

```powershell
cd F:\blog\backend
.\.venv\Scripts\Activate.ps1

fastapi dev app/main.py           # 开发模式（可能卡住，不推荐）
uvicorn app.main:app --reload     # 开发模式（推荐）
uvicorn app.main:app              # 生产模式
```

### 重置数据库

删除 `backend/blog.db`，重启后端即可重新生成种子数据：

```powershell
del F:\blog\backend\blog.db
```

---

## 技术栈

**前端**
- Vue 3 + TypeScript + Vite
- Vue Router + Pinia
- Axios（HTTP 请求）
- markdown-it + highlight.js（Markdown 渲染）

**后端**
- FastAPI + Pydantic
- SQLAlchemy + SQLite
- python-jose + bcrypt（JWT 认证）
- SECRET_KEY 从环境变量读取

---

## Docker 部署

```powershell
cd F:\blog
docker-compose up --build
```

- 前端：http://localhost（端口 80）
- 后端：http://localhost:6965

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 前端页面空白/加载失败 | 确认后端在 6965 端口运行，检查终端报错 |
| 登录后跳转异常 | 清除 localStorage：浏览器控制台执行 `localStorage.clear()` |
| 文章编辑页 404 | 确认通过后台管理页的「编辑」按钮进入 |
| npm install 报错 | 删除 `node_modules` 和 `package-lock.json` 后重新安装 |
| pip install 报错 | 确认虚拟环境已激活（终端前面有 `(.venv)`） |
| 端口被占用 | 前端改 `vite.config.ts` 的 `server.port`，后端用 `--port` 参数 |

---

## 文件速查

| 需要改什么 | 文件路径 |
|------------|----------|
| 全局颜色/间距/字体 | `frontend/src/assets/styles/variables.css` |
| 全局重置/滚动条/基础样式 | `frontend/src/assets/styles/base.css` |
| 动态背景 | `frontend/src/components/common/AnimatedBackground.vue` |
| 导航栏 | `frontend/src/components/common/AppNavbar.vue` |
| 首页 | `frontend/src/views/HomeView.vue` |
| 后台管理 | `frontend/src/views/AdminView.vue` |
| 关于页面 | `frontend/src/views/AboutView.vue` |
| 写文章 | `frontend/src/views/CreatePostView.vue` |
| 编辑文章 | `frontend/src/views/EditPostView.vue` |
| 路由配置 | `frontend/src/router/index.ts` |
| API 接口（公共） | `frontend/src/api/blog.ts` |
| API 接口（管理） | `frontend/src/api/admin.ts` |
| 类型定义 | `frontend/src/types/blog.ts` |
| 后端路由 | `backend/app/api/v1/endpoints/` |
| 数据库模型 | `backend/app/models/` |
| 种子数据 | `backend/app/db/seed_data.py` |
