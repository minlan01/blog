# Blog 优化施工总览（v2.3 · P0-P3）

> 生成时间：2026-07-25 23:19
> 来源：`D:/blog/docs/OPTIMIZATION_PLAN.md` v2.3
> 用途：P0-P3 的可执行清单，按阶段交付，独立验收
> 总工时：23-32 天（不含 P4 视觉增强弹性段）

---

## 阶段总览

| 阶段 | 主题 | 工时 | 必须前置 |
|------|------|------|---------|
| **P0** | 基线治理 | 2-3 天 | 无 |
| **P1** | 安全与关键修复 | 3-4 天 | P0 完成 |
| **P2** | 内容核心（Markdown/FTS5/编辑器） | 6-8 天 | P1 完成 |
| **P3** | 互动能力 | 5-6 天 | P2 完成 |
| **P4** | 视觉增强（弹性） | 6-9 天 | P3 完成（可并行） |

---

# P0 · 基线治理（2-3 天）

## 目标

把项目从"双迁移路径 + 弱 baseline + 残留依赖"治理到"Alembic 唯一入口 + 真实 root baseline + 干净依赖"。

## 任务清单

### P0-1：Alembic 迁移链完全重建（1.5 天）

**操作**：
1. 归档旧 3 个 revision 到 `backend/alembic/versions/_archive/`
   - `62dbd9b622d0_initial_migration.py`
   - `a3f1c8d4e5b2_add_file_path_to_images.py`
   - `b4c2d9e8f1a0_add_object_storage_fields.py`
2. 手写 `0001_root_baseline.py`：
   - `down_revision = None`
   - 用 `op.create_table()` 显式定义全部核心表（users/posts/categories/tags/comments/messages/friend_links/images/post_revisions/site_configs）
   - 包含所有索引、外键、唯一约束
3. 在空 SQLite 库验证：`alembic downgrade base` → `alembic upgrade head` 完整可跑

**已有库迁移**：
```bash
docker compose stop backend
cp /opt/blog/data/app.db /opt/blog/data/app.db.backup-$(date +%s)
docker compose run --rm backend python -m app.cli diff_schema --full
# 若干净：alembic stamp 0001_root
# 若有差异：停下来手写 align_with_production.py
```

**验收**：
- [ ] 空库 `alembic upgrade head` 建出全部核心表
- [ ] 已有库 `diff_schema --full` exit 0
- [ ] `alembic current` 输出 `0001_root (head)`
- [ ] 旧 revision 在 `_archive/`，不在版本链
- [ ] 数据库行数与迁移前一致
- [ ] `PRAGMA foreign_key_check` 返回空

### P0-2：`diff_schema` CLI 命令（0.5 天）

**新建** `app/cli.py`（首次出现），用 Typer。`diff_schema` 子命令对比 11 个维度：

| 维度 | 比较内容 |
|------|---------|
| tables | 缺失/多余 |
| columns | 缺失/多余 |
| column type | `str(orm_col.type)` vs `db_col["type"]` |
| nullable | `orm_col.nullable` vs `db_col["nullable"]` |
| default | `orm_col.default` vs `db_col["default"]` |
| indexes | 缺失/多余 |
| unique constraints | 缺失/多余 |
| foreign keys | 缺失/多余 |
| check constraints | 缺失/多余 |
| triggers（SQLite） | `sqlite_master WHERE type='trigger'` |
| FTS 虚拟表 | `sqlite_master WHERE sql LIKE '%FTS%'` |

有差异 `exit 1`，无差异 `exit 0`（CI 友好）。

### P0-3：`seed` CLI 命令 + entrypoint 改造（0.3 天）

**新建** CLI `seed` 子命令：
```python
@cli.command()
def seed():
    from app.db.session import SessionLocal
    from app.db.seed_data import seed_database
    with SessionLocal() as db:
        seed_database(db)
```

**改** `entrypoint.sh`：
```sh
alembic upgrade head
python -m app.cli seed
exec "$@"
```

### P0-4：`init_db.py` 移除 `create_all()`（0.2 天）

- `init_db.py:238` 的 `Base.metadata.create_all(bind=engine)` 改为只在 `settings.ENV == "test"` 时调用
- 生产完全依赖 `alembic upgrade head`

### P0-5：MinIO 惰性导入（0.5 天）

**改** `app/services/object_storage.py`：
- `Minio` 和 `S3Error` 都改为函数内延迟导入
- 用 `TYPE_CHECKING` 保住类型提示
- 用 `settings.use_minio`（真实字段，property）做分支判断

**分步验收**（关键：分两步走）：
1. 完成代码改造，`requirements.txt` 保留 `minio`
2. `pip uninstall minio` 后 `python -c "from app.main import app"` 不报错
3. `docker compose up backend`（无 minio 包）启动成功
4. `STORAGE_BACKEND=local` 上传接口测试通过
5. 全部通过 → 才能从 `requirements.txt` 移除 `minio`

### P0-6：生产密码基线（0.2 天）

- `docker-compose.yml` 不带 `ADMIN_DEFAULT_PASSWORD` 默认值
- 只在服务器 `/opt/blog/.env` 明文写一次
- `must_change_password` 默认 `False`，种子管理员显式 `True`

## P0 总验收

- [ ] 空库 `alembic upgrade head` 成功
- [ ] 已有库迁移无报错、行数一致
- [ ] `diff_schema --full` 干净
- [ ] `pip uninstall minio` 后后端启动正常
- [ ] `grep create_all init_db.py` 只在 test 分支
- [ ] 种子管理员首次登录被强制改密

---

# P1 · 安全与关键修复（3-4 天）

## 目标

闭环 4 项安全红警 + 修复 4 项现有 bug + 完成代码卫生。

## 任务清单

### P1-1：强制改密后端中间件（0.5 天）

**改** `app/api/v1/deps.py`：
```python
_ACTIVE_WHITELIST = {
    "/api/v1/auth/change-password",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
}

def require_active_user(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    if user.must_change_password and request.url.path not in _ACTIVE_WHITELIST:
        raise HTTPException(423, "请先修改初始密码")
    return user

def require_super_admin(
    user: User = Depends(require_active_user),  # 叠加检查
) -> User:
    if user.role != "super_admin":
        raise HTTPException(403, "需要超级管理员权限")
    return user
```

**替换点**：
- 所有 `Depends(get_current_user)` → `Depends(require_active_user)`
- `require_super_admin` 内部叠加 `require_active_user`
- 仅改密/登出/我 三个接口保留底层 `get_current_user`

**Alembic migration** `p1_add_must_change_password.py`：
```python
op.add_column("users", sa.Column("must_change_password", sa.Boolean, nullable=False, server_default=sa.false()))
```

### P1-2：refresh_token 两阶段迁移（阶段 1，0.5 天）

**Migration** `p1a_add_refresh_token_hash.py`：
```python
def upgrade():
    op.add_column("users", sa.Column("refresh_token_hash", sa.String(64), nullable=True))
    op.create_index("ix_users_refresh_token_hash", "users", ["refresh_token_hash"])
```

**代码改动**：
- `auth.py` 登录/刷新接口：**双写** refresh_token（旧）+ refresh_token_hash（新）
- `auth.py` token 校验：**双读**，先 hash 后 fallback 明文（兼容期）

**CLI 一次性迁移** `migrate_refresh_tokens`：
```python
@cli.command()
def migrate_refresh_tokens():
    import hashlib
    with SessionLocal() as db:
        users = db.query(User).filter(User.refresh_token.isnot(None)).all()
        for u in users:
            if u.refresh_token:
                u.refresh_token_hash = hashlib.sha256(u.refresh_token.encode()).hexdigest()
                u.refresh_token = None
        db.commit()
```

**阶段 1 验收**：
- [ ] users 表同时存在两字段
- [ ] 所有 `refresh_token` 字段为 NULL
- [ ] 所有 `refresh_token_hash` 是 64 字符或 NULL
- [ ] 登录/刷新接口测试通过
- [ ] `PRAGMA foreign_key_check` 返回空

> 阶段 2（drop 旧字段）放下一维护窗口，间隔 1 周+。

### P1-3：DeepSeek API Key 轮换（用户手动）

- 用户到 DeepSeek 后台生成新 Key
- 旧 Key 立即禁用
- `.env` 从 git 历史 purge：`git filter-repo --path .env --invert-paths`
- `.env` 加入 `.gitignore`

### P1-4：Nginx CSP 修正（0.3 天）

**改** `frontend/nginx.conf`：
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: blob: https:; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'" always;
```

**关键改动**：`img-src` 加 `https:`，允许外部封面/友链头像。

**验收**：在文章列表页看封面正常加载 + 友链页头像正常 + Console 无 CSP violation。

### P1-5：Sitemap / robots 绝对 URL（0.3 天）

- `config.py` 加 `SITE_URL: str = "http://localhost:3710"`（生产改真实域名）
- `sitemap.py` 所有 `<loc>` 拼接 `settings.SITE_URL`
- `robots.txt` 改由后端路由返回（注入 SITE_URL）

### P1-6：版本历史 bug 修复（0.3 天）

**改** `app/services/blog_service.py::create_post`：
```python
def create_post(self, data, tag_ids):
    post = Post(...)
    self.db.add(post)
    self.db.flush()           # 关键：先拿 id
    self._save_revision(post)
    self.db.commit()
    self.db.refresh(post)
```

**回归测试** `test_create_post_revision.py`：
- 创建后 `PostRevision.post_id == post.id` 非 None

### P1-7：补齐现有实现（0.5 天）

- `robots.txt`（已存在）：核对 Disallow + 补 Sitemap 指令
- `sitemap lastmod`（已存在）：改为 W3C ISO 8601 + 加 Cache-Control
- 编辑器图片上传（已存在）：补粘贴事件 + 拖拽高亮
- 版本历史 API（已存在）：补前端抽屉 UI + diff2html 视图 + 回滚确认弹窗

### P1-8：代码卫生（0.5 天）

- 抽 `app/utils/tree.py::collect_descendant_ids`（合并 4 处重复）
- 建 `app/models/_mixins.py::TimestampMixin`
- 建 `app/core/exceptions.py`（BlogError → NotFoundError / PermissionDenied / ValidationError / ConflictError）
- `main.py` 加全局 exception handler，业务代码用 `raise NotFoundError(...)` 替代 `HTTPException(404, ...)`
- CORS `allow_methods` 收紧到 `["GET","POST","PUT","DELETE","PATCH"]`

## P1 总验收

- [ ] 用初始密码登录后调 `/api/v1/admin/posts` 返回 423
- [ ] 用初始密码登录后调 `/api/v1/auth/change-password` 正常
- [ ] 改密后所有接口恢复
- [ ] refresh_token_hash 全是 64 字符或 NULL
- [ ] DeepSeek 旧 Key 已禁用
- [ ] `git log --all -- .env` 不再有明文 Key
- [ ] 文章列表页封面正常加载，Console 零 CSP 报错
- [ ] 编辑器粘贴/拖拽图片正常
- [ ] 版本历史抽屉能看 diff、能回滚
- [ ] `git grep "_collect_.*_descendant_ids"` 只有 utils/tree.py 一处
- [ ] `curl https://domain/api/v1/sitemap.xml` 返回的 `<loc>` 是绝对 URL
- [ ] 创建文章后 PostRevision.post_id 非 None

---

# P2 · 内容核心（6-8 天）

## 目标

统一后端 Markdown 渲染（含兼容契约）+ 上 FTS5 全文搜索 + 编辑器升级。

## 任务清单

### P2-1：后端 Markdown 渲染管线（2-3 天）

**新建** `app/services/markdown_renderer.py`：

技术栈：`mistune` 3.x + `Pygments` + `nh3`

**渲染管线**：
```
Markdown → mistune → HTML → Pygments 高亮 → nh3 消毒 → content_html (存 DB)
                                                          ↓
                                                    前端仅 v-html 渲染
```

**7 条兼容契约**（必须满足，否则功能回归）：

| 现有功能 | 保障方式 |
|---------|---------|
| 脚注 `[^1]` | 启用 `mistune.plugins.footnotes` |
| 标题 slug 生成 | 自定义 renderer，heading 生成 `id="{slug(title)}"` |
| TOC 依赖标题 ID | 后端同步产出 TOC JSON，缓存到 `Post.toc_json` |
| 图片 img src | nh3 白名单 `img[src]`，src 前缀白名单（本站/data:/https:） |
| 外链 `<a>` | 后处理加 `rel="nofollow noopener external"` + `target="_blank"` |
| 表格 / 删除线 / 任务列表 | 启用 `mistune.plugins.table`/`strikethrough`/`task_lists` |
| 代码块 | Pygments HtmlFormatter，输出 `<pre class="highlight">` |

**Post 模型变更**：
```python
content_markdown: Mapped[str]          # 原文
content_html: Mapped[str]              # 新：消毒后 HTML
toc_json: Mapped[str]                  # 新：TOC JSON
content_html_version: Mapped[int] = 1  # 新：渲染管线版本号
```

**CLI** `rerender_all`：遍历所有 Post 重新渲染，加 tqdm 进度条。首次上线必须跑一次。

**渲染入口**：
```python
def render(md: str) -> tuple[str, list[dict]]:
    """返回 (content_html, toc)"""
    ...
```

`blog_service.create_post` / `update_post` 保存时调用。

**7 条回归测试** `test_markdown_render.py`：
- `test_footnote_preserved`
- `test_heading_slug_stable`（同标题多次渲染 slug 一致）
- `test_toc_json_matches_headings`
- `test_external_link_rel`
- `test_img_src_whitelist`（javascript: / vbscript: 被剥离）
- `test_code_block_highlighted`（Python 代码块含 `<span class="k">def</span>`）
- `test_xss_blocked`（`<script>` 被 nh3 剥离）

**前端改动**：
- 移除 `highlight.js`
- 文章详情页从 `content_html` 渲染，无客户端 markdown-it
- 深/浅色主题下代码块自动切换（用 `code-light.css` / `code-dark.css` + `data-theme` 切换）

### P2-2：SQLite FTS5 全文搜索（2 天）

**Migration** `p2_create_posts_fts.py`：
```python
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return  # 方言判断
    op.execute("CREATE VIRTUAL TABLE posts_fts USING fts5("
               "title, summary, content_text, "
               "tokenize='unicode61 remove_diacritics 2')")

def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    op.execute("DROP TABLE IF EXISTS posts_fts")
```

**新建** `app/services/fts_sync.py`：
- 用 SQLAlchemy event listener（after_insert / after_update / after_delete）
- jieba 分词后存到 FTS
- 应用层 delete + insert（不用 SQL 触发器，避免双职责冲突）

**批量删除修正**（关键）：
```python
# admin.py 批量删除改为逐条 delete（触发 ORM event）
posts = db.query(Post).filter(Post.id.in_(ids)).all()
for post in posts:
    db.delete(post)
db.commit()
```

> 批量 > 100 条时走显式 FTS 批量删除：
> ```python
> ids_to_delete = [p.id for p in posts]
> db.query(Post).filter(Post.id.in_(ids_to_delete)).delete(synchronize_session=False)
> db.execute(text("DELETE FROM posts_fts WHERE rowid IN :ids").bindparams(...), {"ids": ids_to_delete})
> ```

**查询 API**（`/api/v1/search`）：
- `escape_fts_query` 函数：jieba 分词后每个词用双引号包裹 + `OR` 连接
- FTS5 特殊字符 `"` `(` `)` `*` `-` `+` `^` 转义
- `OperationalError` 兜底（语法错误返回空结果）
- `snippet()` 函数返回带 `<mark>` 高亮的片段

**CLI** `rebuild_fts`：全量重建 FTS 索引。首次上线必须跑一次。

**6 条测试**：
- `test_fts_insert.py` — 新增 post 后能被搜到
- `test_fts_update.py` — 修改 post 后旧 title 搜不到、新 title 能搜到
- `test_fts_delete.py` — 删除 post 后搜不到
- `test_fts_bulk_delete_syncs.py` — 批量删除后 posts_fts 不残留
- `test_fts_special_chars.py` — 用户输入 `"` `*` `(` 不炸
- `test_fts_empty.py` — 空查询返回空结果不报错

### P2-3：编辑器升级（2-3 天）

- **AI 辅助面板**：调用现有 DeepSeek，按钮"润色本段/生成摘要/生成 SEO 描述/翻译为英文"
- **IndexedDB 自动保存草稿**：每 5 秒存一次，打开时检测并恢复
- **粘贴图片上传**：监听 paste 事件，自动上传 + 插入 markdown
- **拖拽图片上传**：补拖拽区域高亮反馈
- **Ctrl+K 命令面板**：用 Fuse.js 模糊匹配，跳转任意文章/切分类/新建
- **版本历史 UI**：右侧抽屉 + diff2html 视图 + 回滚确认

## P2 总验收

- [ ] 后端 `content_html` 字段填充完毕（所有历史文章）
- [ ] `python -m app.cli rerender_all` 幂等可重复运行
- [ ] 前端文章详情页从 `content_html` 渲染，无客户端 markdown-it
- [ ] 深/浅色主题下代码块自动切换配色
- [ ] 7 条 Markdown 兼容契约测试全部通过
- [ ] 搜索 "vue" / "响应式" / "Docker" 都能命中
- [ ] 搜索包含特殊字符（引号、括号）不报错
- [ ] 6 条 FTS 测试全部通过
- [ ] 编辑器 Ctrl+K / 粘贴图片 / AI 润色 / 版本历史全部可用

---

# P3 · 互动能力（5-6 天）

## 目标

加 4 个互动功能 + 完整测试 + CLI/crontab 定时任务。

## 任务清单

### P3-1：点赞 / 收藏（1 天）

**新表** `post_reactions`：
```
id, post_id (FK), user_id (FK), type ('like'|'bookmark'), created_at
UNIQUE(post_id, user_id, type)
INDEX(user_id, type)
INDEX(post_id, type)
```

**API**：
- `POST   /api/v1/posts/{id}/reactions` body: `{type: 'like'}`
- `DELETE /api/v1/posts/{id}/reactions/{type}`
- `GET    /api/v1/me/bookmarks`

**并发防护**：
- `INSERT ... ON CONFLICT DO NOTHING` 幂等
- 30 秒频控防反复点
- `DELETE` 幂等（删不存在的行也返回 200）

**测试**：
- `test_reaction_idempotent.py`
- `test_reaction_concurrent.py`

**前端**：文章卡片右下角点赞按钮 + 心跳粒子动画（Motion One）+ ProfileView 加"我的收藏"Tab

### P3-2：评论表情反应（1 天）

**新表** `comment_reactions`：
```
id, comment_id (FK), user_id (FK), emoji (VARCHAR 8), created_at
UNIQUE(comment_id, user_id, emoji)
```

emoji 白名单硬编码：`👍 ❤️ 😂 🎉 🚀 👀`

**前端**：评论底部一排 6 个按钮 + 计数，悬停浮出反应者。

### P3-3：邮件订阅（1.5 天）

**新表** `subscribers`：
```
id, email (UNIQUE), confirm_token_hash (VARCHAR 64), confirm_expires_at,
confirmed (DEFAULT 0), unsubscribe_token_hash (VARCHAR 64),
last_unsubscribe_at, created_at, confirmed_at, last_sent_at
```

**关键设计**（v2.3 安全强化）：
- token 只存 sha256 哈希，泄露 DB 也无法伪造
- `confirm_expires_at` 24 小时过期
- 未确认订阅 30 天后自动清理
- 退订频率限制：24 小时内同一邮箱最多 3 次

**流程**：
1. 用户填邮箱 → POST → 生成原始 token，存 hash，发确认邮件
2. 用户点确认链接 → POST → 设 confirmed=1
3. 周报发送：CLI `send_digest --days 7` 拉取近 7 天新文章
4. 每封邮件末尾附退订链接

**CLI**：
```python
@cli.command()
def send_digest(days: int = 7, dry_run: bool = False, limit: int = 50): ...

@cli.command()
def cleanup_pending_subscribers(): ...
```

**Crontab**：
```cron
0 20 * * 0  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli send_digest'
30 3 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_pending_subscribers'
```

**前端**：右侧栏新增 `SubscribeWidget.vue`

### P3-4：阅读足迹（1.5 天）

**新表 `read_track_events`**（幂等事件表）：
```
post_id, session_id (VARCHAR 64), window_start (DATETIME), event_type ('view'|'finished')
UNIQUE(post_id, session_id, window_start, event_type)
```

**新表 `post_read_stats`**（聚合表）：
```
post_id (PK, FK), read_seconds (INT DEFAULT 0), finished_count (INT DEFAULT 0), updated_at
```

**上报接口** `POST /api/v1/posts/{id}/read-track`：
- Body: `{session_id, duration_ms, finished}`
- 后端计算 `window_start = floor(now / 30min)`
- `INSERT ... ON CONFLICT DO NOTHING` 插入 events
- 插入成功 → 更新聚合表；冲突 → 跳过

**前端采集**：
- 文章详情页 mount 时记录 startTime
- IntersectionObserver 监听文末元素 → 触发"完成阅读"
- `visibilitychange` 离开页面时上报 duration
- session_id 由 `crypto.randomUUID()` 生成，存 sessionStorage

**CLI**：
```python
@cli.command()
def cleanup_read_events(days: int = 7): ...
```

**Crontab**：
```cron
0 4 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_read_events --days 7'
```

**前端展示**：文末"X 人读过 · 平均阅读 Y 分钟"

### P3-5：Crond 定时任务清单（0.2 天）

部署到服务器后用 `crontab -e` 添加：

```cron
# 每天 3:00 清理旧版本
0 3 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_revisions'

# 每天 3:30 清理未确认订阅
30 3 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_pending_subscribers'

# 每天 4:00 清理 7 天前阅读事件
0 4 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_read_events --days 7'

# 每周日 20:00 推送订阅周报
0 20 * * 0  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli send_digest'
```

## P3 总验收

- [ ] 未登录点赞跳登录
- [ ] 重复点赞不产生新行（UNIQUE 约束生效）
- [ ] 收藏列表能看到自己收藏的文章
- [ ] 评论 emoji 反应可点、可取消
- [ ] emoji 白名单外的输入被拒
- [ ] 邮件订阅 token 数据库存的是哈希
- [ ] 确认链接 24 小时后失效
- [ ] 未确认订阅 30 天后自动清理
- [ ] `send_digest --dry-run` 打印近 7 天新文章列表
- [ ] 退订 24 小时内最多 3 次切换
- [ ] 阅读上报两个 worker 各调 10 次，`post_read_stats` 只累计一次
- [ ] 事件表 UNIQUE 约束真的生效（并发测试）
- [ ] 文章底部"X 人读过"数字随访问增长
- [ ] 4 条 crontab 全部添加到 `crontab -l` 输出

---

# 跨阶段：每次部署前回归

无论部署哪个阶段，部署前必跑：

- [ ] 登录 / 注册 / 登出 正常
- [ ] 文章列表 / 详情 / 分类 / 标签 无 500
- [ ] 评论 / 留言 / 友链 正常
- [ ] 后台各 Tab 无 500
- [ ] AI 对话可用
- [ ] `docker compose logs backend` 无 ERROR
- [ ] 浏览器 Console 无 error 红线
- [ ] Lighthouse Performance ≥ 85（首页）
- [ ] `alembic current` 输出 head 版本
- [ ] `diff_schema --full` 干净

---

# 阶段交付节奏

```
Week 1
  Day 1-3   P0 基线治理
  Day 4     部署验证 P0（无回归）
  Day 5-7   P1 安全 + 关键修复

Week 2
  Day 8     部署验证 P1 + refresh_token 阶段 1
  Day 9-11  P2 后端 Markdown 渲染 + 兼容契约测试
  Day 12-13 P2 FTS5 + 编辑器

Week 3
  Day 14    P2 部署 + rerender_all + rebuild_fts
  Day 15-17 P3 点赞/表情/订阅/阅读统计
  Day 18    P3 部署 + Crontab 配置
  Day 19    refresh_token 阶段 2（drop 旧字段）
```

**总计 P0-P3**：约 19 个工作日，加上弹性缓冲约 23-32 天。

---

# 立即开工第一步

如果确认按此计划执行，**P0-1（Alembic 迁移链重建）** 立刻起手：

1. 备份当前数据库
2. 归档旧 3 个 revision
3. 写 `0001_root_baseline.py`（手写全表）
4. 空库测试 `alembic upgrade head`
5. 已有库测试 `diff_schema --full` 干净
6. stamp 到 0001_root

确认后告诉我"开工"，我开始执行 P0-1。
