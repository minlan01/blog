# Blog 全面优化 · 执行方案 v2.2（二次审核修订版）

> 生成时间：2026-07-25 22:38
> 状态：修复 v2.1 二次审核的 12 项问题（P0×2 / P1×7 / P2×3）
> 前置版本：v2.1

---

## 版本差异（v2.1 → v2.2）

| # | 二次审核问题 | v2.2 处理 |
|---|-------------|-----------|
| P0-1 | Alembic 基线 stamp head 会掩盖差异（初始 migration 只建 friend_links + view_count） | **重造真实 baseline**：新建 `p0_baseline.py`，autogenerate 出完整 schema；已有库先备份+对比再决定 |
| P0-2 | `python -m app.db.seed` 命令不存在 | 改为 CLI 命令 `python -m app.cli seed`（内部调用现有 `seed_database()`） |
| P1-3 | MinIO 惰性导入示例错误：`storage_backend` 字段名错、S3Error 也需延迟导入 | 使用真实字段 `settings.STORAGE_BACKEND` / `settings.use_minio`；`Minio` 和 `S3Error` 都改为函数内延迟导入 |
| P1-4 | `require_active_user` 用了未定义的 `request`；`require_super_admin` 会绕过 | Depends 里注入 `request: Request`；`SuperAdmin` 也走 active-user 检查 |
| P1-5 | SQLite 不支持 `ALTER COLUMN`，refresh_token 迁移方案不可执行 | 用 `op.batch_alter_table` 或"新字段 + 拷贝 + 删旧字段"两步走 |
| P1-6 | FTS5 event listener 漏掉 `Query.delete()` 批量删除 | 后台批量删除改为逐条 delete + 显式同步 FTS；migration 加 SQLite 方言判断 |
| P1-7 | 后端 Markdown 迁移会丢失现有功能（脚注、外链、标题ID、TOC） | 补齐兼容性契约：脚注插件、slug 生成器、rel=noopener、image src 白名单，附回归测试 |
| P1-8 | 壳页面示例引用不存在的 `settings.site_url` / `settings.site_name`；后端容器没有 `index.html` | 新增 `SITE_URL` 配置 + 从 DB 读 SiteConfig；构建时把 `frontend/dist/index.html` 复制到后端 image 里 |
| P1-9 | 阅读统计 session_id 幂等在多 worker 不可靠 | 建 `read_track_events(post_id, session_id, window_start)` 表 + UNIQUE 约束，持久化幂等 |
| P2-10 | 创建文章 `_save_revision` 在 `post.id` 未 flush 时调用 | 修 `blog_service.create_post`：先 `db.add + db.flush()` 拿到 id，再存 revision |
| P2-11 | Sitemap / robots 使用相对 URL | 全部改绝对 URL（用 `SITE_URL` 或 request base_url） |
| P2-12 | 订阅 token 明文存储、无过期 | 只存 sha256 哈希 + 加过期字段 + 退订频率限制 |

---

## 目录

1. [用户抉择快照](#一用户抉择快照)
2. [P0 基线治理（重写）](#二p0-基线治理重写)
3. [P1 安全与关键修复](#三p1-安全与关键修复)
4. [P2 内容核心](#四p2-内容核心)
5. [P3 互动能力](#五p3-互动能力)
6. [P4 视觉增强](#六p4-视觉增强)
7. [依赖变更清单](#七依赖变更清单)
8. [Alembic 治理规范](#八alembic-治理规范)
9. [CLI + Crontab](#九cli--crontab)
10. [时间预算](#十时间预算)
11. [验收清单](#十一验收清单)
12. [附录](#十二附录)

---

## 一、用户抉择快照

| # | 抉择项 | 决定 |
|---|--------|------|
| 1 | Shiki 替换 highlight.js | 改为**后端 mistune + Pygments** |
| 2 | 点赞/邮件订阅新增表 | ✅ |
| 3 | 不引入 APScheduler | ✅ Linux crontab + Typer CLI |
| 4 | FTS5 全文搜索 | ✅ 应用层 event + 显式同步 + SQLite-only |
| 5 | View Transitions 主题切换 | ✅ 放弃 Safari 17- |

---

## 二、P0 基线治理（重写）

### 2.1 Alembic 真实 baseline 生成

**问题回顾**：现有 `62dbd9b622d0_initial_migration.py` 只建了 `friend_links` 表 + 加了 `posts.view_count` 列，核心表 (users/posts/categories/tags/comments 等) 从未通过 Alembic 建过——它们是 `init_db.py` 里 `Base.metadata.create_all()` 建的。因此：
- 空库 `alembic upgrade head` 会失败（缺 posts 表就无法 `add_column view_count`）
- 已有库 `alembic stamp head` 会掩盖字段偏差

**v2.2 方案**：重造真实 baseline，不删旧 revision，做补充。

```
alembic/versions/
  62dbd9b622d0_initial_migration.py       (旧的，保留但内部改幂等)
  a3f1c8d4e5b2_add_file_path_to_images.py (同样加幂等保护)
  b4c2d9e8f1a0_add_object_storage_fields.py (同上)
  p0_true_baseline.py                     (新增：全部核心表，幂等)
```

**具体流程**：
1. 开发机空 SQLite 库跑 `Base.metadata.create_all()` 建全表作参考
2. 手写 `p0_true_baseline.py`，逐一 `op.create_table()`
3. `down_revision = "b4c2d9e8f1a0"`，内部所有 `create_table` 前先 `inspector.has_table()` 判断
4. 已有库跑 `alembic upgrade head` → 表都在，全部 no-op，只写入 `alembic_version`
5. 空库跑 `alembic upgrade head` → 走旧 migration + baseline → 建全表

**幂等 create_table 骨架**：
```python
from sqlalchemy import inspect

def _has_table(name: str) -> bool:
    return inspect(op.get_bind()).has_table(name)

def upgrade():
    if not _has_table("users"):
        op.create_table("users", ...)
    if not _has_table("categories"):
        op.create_table("categories", ...)
    # 每张核心表都这样判断
```

**已有库对比校验**（部署前一次性）：
```bash
cp /opt/blog/data/app.db /opt/blog/data/app.db.backup-$(date +%s)
docker compose exec backend python -m app.cli diff_schema
```

`diff_schema` CLI 命令新增：反射数据库比对 `Base.metadata`，报告缺失字段/表。

**验收**：
- [ ] 空库 `alembic upgrade head` 建出全部核心表
- [ ] 已有库 `alembic upgrade head` 无报错、schema 无变化
- [ ] `diff_schema` 报告干净

### 2.2 seed 命令改造

v2.1 里 `python -m app.db.seed` 不存在。v2.2 走 CLI 调用已有的 `seed_database()`：

```python
# app/cli.py
@cli.command()
def seed():
    from app.db.session import SessionLocal
    from app.db.seed_data import seed_database
    with SessionLocal() as db:
        seed_database(db)
```

`entrypoint.sh`：
```sh
alembic upgrade head
python -m app.cli seed
exec "$@"
```



### 2.3 MinIO 惰性导入（真实字段名）

审核指出：v2.1 示例用了不存在的 `settings.storage_backend`。核实后正确字段：
- `settings.STORAGE_BACKEND: str = "local"`
- `settings.use_minio: bool`（property）

**完整改法**：

```python
# app/services/object_storage.py
from __future__ import annotations
from typing import TYPE_CHECKING
from app.core.config import settings

if TYPE_CHECKING:
    from minio import Minio as _Minio

class ObjectStorage:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from minio import Minio       # 延迟
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client

    def upload(self, ...):
        from minio.error import S3Error  # 也要延迟
        try:
            ...
        except S3Error as exc:
            ...

def get_object_storage():
    if settings.use_minio:
        return ObjectStorage()
    return None
```

**关键更正**：
- `Minio` 和 `S3Error` 都要延迟（v2.1 只延迟 Minio 是错的）
- 用 `TYPE_CHECKING` 保住类型提示

**分步验收**：
1. 完成代码改造，requirements.txt 保留 minio
2. `pip uninstall minio` 后 `python -c "from app.main import app"` 不报错
3. `docker compose up backend`（无 minio 包）启动成功
4. `STORAGE_BACKEND=local` 上传接口测试通过
5. 全部通过 → 再从 requirements.txt 移除 minio

### 2.4 生产密码

同 v2.1：
- docker-compose.yml 不带默认密码
- 只有服务器 /opt/blog/.env 明文一次
- `must_change_password` 默认 False，种子管理员显式 True

---

## 三、P1 安全与关键修复

### 3.1 强制改密（修正后）

**审核指出**：v2.1 的 `require_active_user` 用了未定义的 `request`；且 `require_super_admin` 独立走 `get_current_user`，管理员路由会绕过。

**v2.2 完整方案**：

```python
# app/api/v1/deps.py
from fastapi import Depends, HTTPException, Request

_ACTIVE_WHITELIST = {
    "/api/v1/auth/change-password",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
}

def get_current_user(...) -> User:
    """底层：只做 token 校验"""
    ...

def require_active_user(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    if user.must_change_password and request.url.path not in _ACTIVE_WHITELIST:
        raise HTTPException(423, "请先修改初始密码")
    return user

def require_super_admin(
    user: User = Depends(require_active_user),  # 关键：叠加检查
) -> User:
    if user.role != "super_admin":
        raise HTTPException(403, "需要超级管理员权限")
    return user
```

**替换点**：
- 所有 `Depends(get_current_user)` → `Depends(require_active_user)`
- `require_super_admin` 内部换成 `Depends(require_active_user)`
- 只有改密/登出/我 保留底层 `get_current_user`

**验收**：
- [ ] 初始密码登录后调 `/api/v1/admin/posts` 返回 423
- [ ] 初始密码登录后调 `/api/v1/auth/change-password` 正常
- [ ] 改密后所有接口恢复

### 3.2 refresh_token 迁移（SQLite 兼容）

**审核指出**：SQLite 不支持 `ALTER COLUMN ... RENAME`。

**v2.2 方案：`batch_alter_table`**：

```python
def upgrade():
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "refresh_token",
            new_column_name="refresh_token_hash",
            type_=sa.String(64),
            existing_nullable=True,
        )
    op.execute("UPDATE users SET refresh_token_hash = NULL")

def downgrade():
    op.execute("UPDATE users SET refresh_token_hash = NULL")
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "refresh_token_hash",
            new_column_name="refresh_token",
            type_=sa.String(500),
            existing_nullable=True,
        )
```

`batch_alter_table` 在 SQLite 下自动"新建表→拷贝→删旧→改名"。

**必须验证**：
- [ ] 本地 SQLite 库 `alembic upgrade head` 无报错
- [ ] `alembic downgrade -1` 也无报错
- [ ] 字段是 VARCHAR(64) 且值全为 NULL

### 3.3 DeepSeek API Key

同 v2.1（不变）。

### 3.4 Nginx CSP

同 v2.1：`img-src 'self' data: blob: https:`，验收看实际图片加载。

### 3.5 修复现有实现

**A. Sitemap / robots 绝对 URL（新增修正项）**

审核指出：v2.1 里 `<loc>` 是相对路径。改法：
- `config.py` 加 `SITE_URL: str = "http://localhost:3710"`（生产改真实域名）
- `sitemap.py` 所有 `<loc>` 拼接 `settings.SITE_URL`
- `robots.txt` 改由后端路由返回（模板注入 SITE_URL 生成绝对 URL）

**B. 版本历史 bug 修复（新增修正项）**

审核指出：`blog_service.create_post` 在 `db.add()` 后立即 `_save_revision(post)`，此时 `post.id` 未 flush，revision 的 `post_id=None`。

**修法**：
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
- 创建文章后 `PostRevision.post_id == post.id` 且非 None

**C. robots.txt / sitemap lastmod / 图片上传（补 UI）**

同 v2.1。

### 3.6 代码卫生

同 v2.1（不变）。


---

## 四、P2 内容核心

### 4.1 后端 Markdown 渲染（补齐兼容性契约）

**审核指出**：v2.1 只写了 mistune + Pygments + nh3，没规定脚注插件、标题 ID、外链安全、图片处理。切换会导致现有 TOC/脚注功能回归。

**v2.2 兼容性契约**（渲染管道必须满足）：

| 现有功能 | v2.2 保障方式 |
|---------|--------------|
| 脚注 `[^1]` | 启用 `mistune.plugins.footnotes` |
| 标题 slug 生成 | 自定义 renderer，heading 时生成 `id="{slug(title)}"`，与前端 TOC 一致 |
| TOC 依赖标题 ID | 后端渲染时同步产出 TOC JSON，缓存到 `Post.toc_json` |
| 图片 img src | nh3 白名单 `img[src]`，src 前缀白名单：本站 / data: / https: |
| 外链 `<a>` | 后处理加 `rel="nofollow noopener external"` + `target="_blank"` |
| 表格 / 删除线 / 任务列表 | 启用 `mistune.plugins.table`、`strikethrough`、`task_lists` |
| 代码块 | Pygments HtmlFormatter(cssclass, linenos=False) 输出 `<pre class="highlight">` |
| 数学公式 | 保留 `$...$` 原文，前端仍用 KaTeX 客户端渲染（若原本有） |

**必须的回归测试** `test_markdown_render.py`：
- `test_footnote_preserved` — `[^1]` 生成 `<sup>` 且反向锚点
- `test_heading_slug_stable` — 相同标题多次渲染 slug 一致
- `test_toc_json_matches_headings` — TOC JSON 项数与文档 `<h1>-<h6>` 数一致
- `test_external_link_rel` — 外链有 `rel="nofollow noopener"`
- `test_img_src_whitelist` — javascript: / vbscript: 前缀被剥离
- `test_code_block_highlighted` — Python 代码块含 `<span class="k">def</span>`
- `test_xss_blocked` — `<script>alert(1)</script>` 被 nh3 剥离

**渲染入口**：
```python
# app/services/markdown_renderer.py
def render(md: str) -> tuple[str, list[dict]]:
    """返回 (content_html, toc)"""
    ...
```

`blog_service.create_post` / `update_post` 保存时调用，写入 `content_html` 和 `toc_json`。

### 4.2 SQLite FTS5（修正批量删除 + 方言判断）

**审核指出两处**：
1. `Query.delete()` 不触发 ORM `after_delete` 事件，`posts_fts` 会残留
2. FTS5 是 SQLite 专用，migration 需要方言判断

**v2.2 方案**：

**A. 批量删除改造**（`admin.py` 相关代码）：
```python
# ❌ 老写法（bypass event）
db.query(Post).filter(Post.id.in_(ids)).delete(synchronize_session=False)

# ✅ v2.2 写法（触发 event，逐条删）
posts = db.query(Post).filter(Post.id.in_(ids)).all()
for post in posts:
    db.delete(post)          # 触发 after_delete → FTS 同步
db.commit()
```

**性能兜底**：批量 > 100 条时，改为"先记 id → 批量删主表 → 显式批量删 posts_fts"：
```python
ids_to_delete = [p.id for p in posts]
db.query(Post).filter(Post.id.in_(ids_to_delete)).delete(synchronize_session=False)
db.execute(text("DELETE FROM posts_fts WHERE rowid IN :ids").bindparams(bindparam("ids", expanding=True)), {"ids": ids_to_delete})
```

**B. FTS migration 加方言判断**：
```python
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return  # 非 SQLite 不建 FTS
    op.execute("CREATE VIRTUAL TABLE ...")

def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    op.execute("DROP TABLE IF EXISTS posts_fts")
```

**C. 明确声明 SQLite-only**：
- `README.md` / `docs/ARCHITECTURE.md` 写明"当前生产环境 SQLite；FTS 功能仅在 SQLite 下启用"
- 若未来切 MySQL，FTS 需重新设计（Elasticsearch / MySQL ngram）

**FTS 事件同步同 v2.1**（应用层 delete+insert + jieba）。

**必须的测试**：
- `test_fts_bulk_delete_syncs.py` — 批量删除后 posts_fts 不残留
- `test_fts_special_chars.py` — 特殊字符不炸
- 其它同 v2.1

### 4.3 编辑器升级

同 v2.1（不变）：AI 面板 / IndexedDB 草稿 / 粘贴上传 / Ctrl+K / 版本历史 UI（bug 已在 3.5.B 修）。



---

## 五、P3 互动能力

### 5.1 点赞 / 收藏

同 v2.1（不变）：
- 表结构 + UNIQUE + INDEX
- `INSERT ... ON CONFLICT DO NOTHING` 幂等
- 并发测试用例

### 5.2 评论表情反应

同 v2.1（不变）。

### 5.3 邮件订阅（token 哈希 + 过期 + 频率限制）

**审核指出**：v2.1 `confirm_token` / `unsubscribe_token` 明文存储，且无过期。

**v2.2 修正后的表结构**：
```
subscribers
  id                     INTEGER PK
  email                  VARCHAR(255) UNIQUE
  confirm_token_hash     VARCHAR(64)      -- sha256(token)
  confirm_expires_at     DATETIME         -- 24 小时后过期
  confirmed              BOOLEAN DEFAULT 0
  unsubscribe_token_hash VARCHAR(64)      -- sha256(token)，长期有效
  last_unsubscribe_at    DATETIME NULL    -- 退订频率限制
  created_at             DATETIME
  confirmed_at           DATETIME NULL
  last_sent_at           DATETIME NULL
```

**流程**：
1. 订阅时生成原始 token（`secrets.token_urlsafe(32)`），存 hash，发信里带原始 token
2. 用户点确认链接 → 后端把原始 token hash 后比对
3. `confirm_expires_at` 超期则返回"确认链接已过期，请重新订阅"
4. 未确认订阅 30 天后自动清理（CLI `cleanup_pending_subscribers`）

**幂等**：
- 已订阅邮箱重复请求订阅 → 返回 202（不新增行，不发新确认信）
- 未确认邮箱重复请求 → 复用旧 token 或重发（限 5 分钟一次）

**退订频率限制**：
- 24 小时内同一邮箱最多 3 次退订/重订切换
- 通过 `last_unsubscribe_at` + 计数字段实现

### 5.4 阅读足迹（跨 worker 持久化幂等）

**审核指出**：v2.1 用 session_id + 短 TTL 内存缓存，两个 worker 各持一份，重复上报会累计。

**v2.2 方案：持久化幂等表**：

```
read_track_events
  post_id      INTEGER
  session_id   VARCHAR(64)
  window_start DATETIME     -- 30 分钟窗口起点（取整）
  event_type   VARCHAR(16)  -- 'view' | 'finished'
  created_at   DATETIME
  UNIQUE(post_id, session_id, window_start, event_type)
```

**上报流程**：
1. 前端 `POST /api/v1/posts/{id}/read-track` body: `{session_id, duration_ms, finished}`
2. 后端计算 `window_start = floor(now / 30min)`
3. `INSERT ... ON CONFLICT DO NOTHING` 插入 events（对同一窗口去重）
4. 若插入成功（`ROWCOUNT=1`）→ 更新 `post_read_stats` 聚合
5. 若冲突 → 跳过（无累计）

**保留 `post_read_stats` 单表存聚合值**（同 v2.1）。

**表清理**：CLI `cleanup_read_events(days=7)`，每天保留 7 天原始 events。

### 5.5 验收（P3）

- [ ] 邮件订阅 token 数据库存的是哈希，非明文
- [ ] 确认链接 24 小时后失效
- [ ] 未确认订阅 30 天后自动清理
- [ ] 阅读上报两个 worker 各调 10 次，`post_read_stats` 只累计一次
- [ ] 事件表 UNIQUE 约束真的生效（并发测试）

---

## 六、P4 视觉增强

### 6.1 View Transitions API

同 v2.1（不变）：主题切换圆形展开 + 卡片共享元素 + Router 显式包裹。

### 6.2 文章壳页面（补齐可运行边界）

**审核指出**：v2.1 示例引用 `settings.site_url` / `settings.site_name` 不存在；后端容器没有前端 `index.html`。

**v2.2 补齐**：

**A. 配置补充**：
```python
# app/core/config.py
SITE_URL: str = "http://localhost:3710"  # 生产改真实域名
# 站点名不加 config，改从 DB SiteConfig 表读
```

**B. Dockerfile 复制前端资产到后端 image**：
```dockerfile
# backend/Dockerfile
COPY --from=frontend-builder /app/dist/index.html /app/spa_shell/index.html
```
或部署脚本挂载：
```yaml
# docker-compose.yml
volumes:
  - ./frontend/dist/index.html:/app/spa_shell/index.html:ro
```

**C. 壳页面路由**（挂在 backend，路径不含 `/api/v1/` 前缀）：
```python
# app/api/shell.py（新增，不属于 v1 前缀）
from fastapi.responses import HTMLResponse
from app.db.session import SessionLocal
from app.models.site_config import SiteConfig

router = APIRouter()

@router.get("/posts/{slug}", response_class=HTMLResponse)
def post_shell(slug: str, db: DBSession):
    post = db.query(Post).filter_by(slug=slug, status="published").first()
    site = db.query(SiteConfig).first()
    site_name = site.site_name if site else "Blog"

    with open("/app/spa_shell/index.html", encoding="utf-8") as f:
        shell = f.read()

    if not post:
        return HTMLResponse(shell, status_code=404)

    og_image = f"{settings.SITE_URL}/api/v1/posts/{post.id}/og.png"
    canonical = f"{settings.SITE_URL}/posts/{slug}"

    meta = f'''<title>{escape(post.title)} - {escape(site_name)}</title>
<meta name="description" content="{escape(post.summary)}"/>
<meta property="og:title" content="{escape(post.title)}"/>
<meta property="og:description" content="{escape(post.summary)}"/>
<meta property="og:image" content="{og_image}"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="{canonical}"/>
<link rel="canonical" href="{canonical}"/>
<meta name="twitter:card" content="summary_large_image"/>'''

    # 用占位符替换（构建时 index.html 里预留 <!-- SEO_META_PLACEHOLDER -->）
    return HTMLResponse(shell.replace("<!-- SEO_META_PLACEHOLDER -->", meta))

# app/main.py
app.include_router(shell_router)  # 不含 v1 前缀，直接挂根路径
```

**D. index.html 占位符**：
```html
<!-- frontend/index.html -->
<head>
  <!-- SEO_META_PLACEHOLDER -->
  <link rel="icon" ...>
</head>
```

**E. Nginx 路由分叉**：
```nginx
# 只有 /posts/{slug} 走后端壳（正则匹配）
location ~ ^/posts/[^/]+$ {
    proxy_pass http://backend:8000;
    proxy_cache post_shell_cache;
    proxy_cache_valid 200 30s;
    proxy_cache_valid 404 10s;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# 资源路径（JS/CSS/图片）继续走前端 static
location /assets/ { ... }
location /images/ { ... }

# 其他 SPA 路由（首页、about、archive 等）继续走前端 static
location / {
    try_files $uri $uri/ /index.html;
}
```

**关键点**：
- 只有 `/posts/{slug}` 路径叉出去；`/posts` 列表页仍走前端
- 静态资源（`/assets/`）从 frontend 服务，壳页面里引用的路径要绝对
- Nginx `proxy_cache` 30 秒短缓存，减轻后端负载

**验收**：
- [ ] 微信内置浏览器发送文章链接，能看到标题和封面预览
- [ ] Twitter Card Validator 通过
- [ ] `curl -A "Twitterbot" https://your-domain/posts/slug` 返回带 og:* 的 HTML
- [ ] 直接浏览器访问文章，页面正常渲染（SPA 挂载成功）

### 6.3 OG 分享图接口

同 v2.1：`GET /api/v1/posts/{id}/og.png` 返回 1200×630 PNG，缓存 30 天。

### 6.4 归档时间线 / 标签知识图谱 / 3D 头像 / 划词 / 404 / 自定义鼠标

同 v2.1（不变）。


---

## 七、依赖变更清单

### 前端 `frontend/package.json`

**新增**（同 v2.1）：
- `motion` ^11.x
- `diff2html` ^3.x
- `fuse.js` ^7.x
- `idb-keyval` ^6.x

**移除**：
- `highlight.js`（后端渲染取代）

**明确不引入**：
- ❌ shiki（改后端 Pygments）

### 后端 `backend/requirements.txt`

**新增**：
- `mistune>=3.0.0,<4.0.0`
- `Pygments>=2.18.0,<3.0.0`
- `nh3>=0.2.0,<1.0.0`
- `jieba>=0.42.0,<1.0.0`
- `python-frontmatter>=1.1.0,<2.0.0`
- `typer>=0.12.0,<1.0.0`
- `tqdm>=4.66.0,<5.0.0`
- `pillow>=10.4.0,<12.0.0`

**惰性导入后暂不移除**：
- `minio`（P0.2.3 完成 5 步验收后移除）
- `pymysql`（同上）

**不引入**：❌ APScheduler ❌ Redis ❌ Meilisearch ❌ Shiki

---

## 八、Alembic 治理规范

### 8.1 目标

- Alembic 是唯一 schema 变更入口
- `init_db.py` 只做种子（且被 CLI seed 命令包装）
- `entrypoint.sh` 自动 `alembic upgrade head` + `python -m app.cli seed`

### 8.2 首次治理（v2.2 关键）

**已有库**：
```bash
# 1. 备份
cp /opt/blog/data/app.db /opt/blog/data/app.db.backup-$(date +%s)

# 2. 对比 schema
docker compose exec backend python -m app.cli diff_schema

# 3. 若报告干净 → 直接 upgrade
docker compose exec backend alembic upgrade head

# 4. 若报告有差异 → 停下来分析，手动补 migration
```

**空库**：
```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.cli seed
```

### 8.3 Migration 清单（一功能一 migration）

| 阶段 | 文件 | 内容 |
|------|------|------|
| P0 | `p0_true_baseline.py` | 幂等创建所有核心表 |
| P1 | `p1_add_must_change_password.py` | users 加字段 |
| P1 | `p1_rename_refresh_token_hash.py` | batch_alter_table 改名 + 清空 |
| P2 | `p2_add_post_content_html.py` | posts 加 content_html / toc_json / content_html_version |
| P2 | `p2_create_posts_fts.py` | SQLite 方言判断建 FTS5 |
| P3 | `p3_create_post_reactions.py` | 点赞/收藏表 |
| P3 | `p3_create_comment_reactions.py` | 评论 emoji 表 |
| P3 | `p3_create_subscribers.py` | 订阅表（含 token hash + 过期字段） |
| P3 | `p3_create_read_track_events.py` | 幂等事件表 |
| P3 | `p3_create_post_read_stats.py` | 阅读聚合表 |

### 8.4 FTS 迁移方言判断

```python
def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    op.execute("CREATE VIRTUAL TABLE posts_fts USING fts5(...)")
```

首次上线后必须运行：
```bash
docker compose exec backend python -m app.cli rebuild_fts
```

---

## 九、CLI + Crontab

### 9.1 CLI 命令集（Typer）

```
app/cli.py
├── diff_schema         # ★新增★ 对比 ORM 与实际 schema
├── seed                # ★新增★ 幂等种子（内部调 seed_database）
├── rebuild_fts         # 全量重建 FTS
├── rerender_all        # 全量重渲染 content_html
├── send_digest         # 订阅周报
├── cleanup_revisions   # 清理旧版本
├── cleanup_pending_subscribers  # ★新增★ 清理未确认订阅
├── cleanup_read_events # ★新增★ 清理阅读事件表
└── create_admin        # 交互式建超管
```

### 9.2 Crontab 示例

```cron
# 3:00 清理旧版本
0 3 * * *  cd /opt/blog && docker compose exec -T backend python -m app.cli cleanup_revisions

# 3:30 清理未确认订阅
30 3 * * *  cd /opt/blog && docker compose exec -T backend python -m app.cli cleanup_pending_subscribers

# 4:00 清理 7 天前的阅读事件
0 4 * * *  cd /opt/blog && docker compose exec -T backend python -m app.cli cleanup_read_events --days 7

# 每周日 20:00 推送订阅周报
0 20 * * 0  cd /opt/blog && docker compose exec -T backend python -m app.cli send_digest
```

**docker/PATH 可靠性提示**：
- 系统 cron 环境很干净，`docker`/`docker compose` 可能不在 PATH
- 用 `bash -lc` 包裹或指定绝对路径：
```cron
0 3 * * *  bash -lc 'cd /opt/blog && /usr/bin/docker compose exec -T backend python -m app.cli cleanup_revisions'
```

---

## 十、时间预算

审核指出 8-12 天严重低估。v2.2 由于新增了 P0 真实 baseline、Markdown 兼容契约、多个测试用例，工时进一步校准：

| 阶段 | 内容 | v2.2 工时 |
|------|------|----------|
| **P0** | 基线治理（真 baseline / seed CLI / MinIO 惰性 / diff_schema） | 2-3 天 |
| **P1** | 强制改密 / refresh_token / CSP / Sitemap 绝对 URL / revision bug / 代码卫生 | 3-4 天 |
| **P2** | Markdown 后端渲染 + 兼容契约 + Pygments + FTS5 + 编辑器 UI + 完整测试 | 6-8 天 |
| **P3** | 点赞 / 表情 / 订阅（token 哈希 + 过期）/ 阅读事件表 + 测试 | 5-6 天 |
| **P4** | View Transitions + 壳页面 + Nginx 路由分叉 + OG 图 + 归档 / 图谱 / 3D | 6-9 天 |

**主线合计：22-30 天**（比 v2.1 的 18-22 天再上浮）。

**建议节奏**：3-4 周主线 + 弹性尾。独立开发者拉长到 5-6 周从容完成。

---

## 十一、验收清单

各阶段独立验收（见对应章节），此处补跨版本回归：

**每次部署前**：
- [ ] 登录 / 注册 / 登出 正常
- [ ] 文章列表 / 详情 / 分类 / 标签 无 500
- [ ] 评论 / 留言 / 友链 正常
- [ ] 后台各 Tab 无 500
- [ ] AI 对话可用
- [ ] `docker compose logs backend` 无 ERROR
- [ ] 浏览器 Console 无 error 红线
- [ ] Lighthouse Performance ≥ 85（首页）
- [ ] Alembic `current` 命令输出 head 版本
- [ ] `diff_schema` 报告干净

---

## 十二、附录

### 附录 A：技术风险与降级

| 风险 | 概率 | 降级 |
|------|------|------|
| p0_true_baseline 忘掉某张表 | 中 | `diff_schema` 命令兜底，部署前必跑 |
| MinIO 惰性后其他模块顶层引用 | 中 | 全局 grep 扫 `^from minio|^import minio` |
| `batch_alter_table` 在旧 SQLite 不支持 | 低 | 至少要 SQLite 3.25，Docker 镜像的 python 版本自带够新 |
| jieba 分词不精 | 中 | 短期够用，用户反馈后可换 pkuseg |
| FTS5 特殊字符 | 中 | `escape_fts_query` 有单元测试覆盖 |
| 壳页面 SEO 与 SPA 挂载冲突 | 中 | Nginx `proxy_cache` + 前端接管路由清 meta |
| Markdown 迁移功能回归 | **高** | 7 条兼容契约测试用例，未通过不允许部署 |
| cron PATH 找不到 docker | 中 | `bash -lc` 包裹 + 绝对路径 |
| 阅读事件表膨胀 | 低 | 每日 CLI 清理 7 天前记录 |
| 订阅 token 泄露 | 低 | 只存 hash，泄露 DB 也无法伪造有效 token |

### 附录 B：明确不做的事

- ❌ 前端 UI 组件库 / Tailwind / SCSS
- ❌ 全站 SSR / Nuxt / SSG（只对 `/posts/{slug}` 做壳）
- ❌ Redis / Celery / RabbitMQ
- ❌ 独立搜索引擎
- ❌ CDN（有域名再谈）
- ❌ A/B 测试 / SaaS 化 / 多语言 SEO
- ❌ 前端 Shiki
- ❌ APScheduler

---

## 变更历史

- **v2.0** (2026-07-25 15:35) — 初版
- **v2.1** (2026-07-25 22:18) — 一次审核修订，12 项
- **v2.2** (2026-07-25 22:38) — 二次审核修订：
  1. Alembic 真实 baseline + diff_schema CLI
  2. seed 命令走 CLI 复用 seed_database
  3. MinIO 惰性用真实字段 `use_minio`，Minio + S3Error 都延迟
  4. `require_active_user` 加 `request: Request`，`require_super_admin` 叠加检查
  5. refresh_token 迁移改 `batch_alter_table`
  6. FTS 批量删除逐条 + 方言判断
  7. Markdown 兼容契约（脚注/slug/TOC/外链/img）+ 回归测试
  8. 壳页面补配置（SITE_URL）+ Dockerfile 复制 index.html + Nginx 路由分叉
  9. 阅读统计改持久化事件表
  10. `create_post` 修 `db.flush()`
  11. Sitemap / robots 绝对 URL
  12. 订阅 token 哈希存储 + 过期字段 + 频率限制
  额外：工时校准 18-22 → 22-30 天

---

_文档 v2.2 · 2026-07-25 22:38_
_下一步：等待用户三次复核后进入 P0 执行。_


---

# v2.3 修订附录（三次审核响应）

> 生成时间：2026-07-25 23:11
> 审核来源：`C:/Users/minlan01/Desktop/BLOG_OPTIMIZATION_REVIEW_2026-07-25.md`
> 三项判定全部成立：P0.2.1 NO-GO / P1.5 Conditional GO / P4.6.2 需补边界
> 本附录**替换** v2.2 中对应章节的相关内容，其余章节保持不变

---

## 修订 1：P0.2.1 Alembic 迁移链完全重建（替换 v2.2 §2.1）

### 三次审核指出的根本问题

v2.2 方案有三个连锁缺陷：

1. `inspector.has_table()` 只能判断"表是否存在"，**无法发现**字段类型、可空性、默认值、索引、唯一约束、外键、检查约束、触发器、视图、FTS 虚拟表的差异
2. `p0_true_baseline.py` 接在 `b4c2d9e8f1a0` 之后，**空库执行 `alembic upgrade head` 时旧 migration 先跑**：`62dbd9b622d0` 会在不存在的 `posts` 表上 `add_column('posts', 'view_count')` → **必然崩溃**
3. `init_db.py:238` 的 `Base.metadata.create_all(bind=engine)` 仍在跑，与"Alembic 是唯一入口"目标冲突

### v2.3 方案：**重建迁移链**

**Step 1 — 归档旧 revision**

将现有 3 个 revision 移动到 `alembic/versions/_archive/`，并在文件顶部加 deprecation 注释。`alembic_version` 表里的 head 标记会被新链覆盖。

```
backend/alembic/versions/
  _archive/
    62dbd9b622d0_initial_migration.py     # archived
    a3f1c8d4e5b2_add_file_path_to_images.py
    b4c2d9e8f1a0_add_object_storage_fields.py
  0001_root_baseline.py                   # 全新起点，down_revision=None
  p1_xxx.py
  p2_xxx.py
  ...
```

**Step 2 — 手写 `0001_root_baseline.py`**

```python
# Revision ID: 0001_root
# Revises: None

from alembic import op
import sqlalchemy as sa

revision = "0001_root"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 全部表用 op.create_table() 显式定义
    # 参考 Base.metadata 的当前状态（autogenerate 后审阅）
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        # ... 完整字段
    )
    # 每张核心表必须包含所有现有索引、外键、唯一约束
    # posts/categories/tags/comments/messages/friend_links/
    # images/post_revisions/site_configs

def downgrade():
    # 按反向顺序 drop 所有表
    pass
```

**关键约束**：
- `down_revision = None`，是新链的真正起点
- 所有现有表、索引、外键、唯一约束**逐一手写**
- 不用 `has_table()` 幂等保护——本 baseline 就是新链的起点，必须从空库建出来
- 写完后立即跑 `alembic downgrade base` → `alembic upgrade head` 验证可重复执行

**Step 3 — 已有库迁移路径**

最危险的一步，必须按顺序执行：

```bash
# 1. 停服
docker compose stop backend

# 2. 双重备份
cp /opt/blog/data/app.db /opt/blog/data/app.db.backup-$(date +%s)
cp /opt/blog/data/app.db /opt/blog/data/app.db.pre_v23

# 3. 全方位 schema 对比
docker compose run --rm backend python -m app.cli diff_schema --full
# 输出: tables/columns/types/nullable/defaults/indexes/unique/FK/check/trigger/FTS

# 4a. 若报告"完全一致" → stamp 到新 root
docker compose run --rm backend alembic stamp 0001_root

# 4b. 若报告有差异 → 停！不能 stamp。生成补齐 migration：
#    alembic revision -m "align_with_production" --autogenerate
#    人工审阅补齐脚本，再 upgrade

# 5. 验证 alembic_version 表
docker compose run --rm backend alembic current
# 应输出 0001_root (head)

# 6. 启服
docker compose up -d backend
```

**Step 4 — `diff_schema` 全方位对比（替换 v2.2 简版）**

CLI 命令需对比以下维度：

| 维度 | ORM 来源 | DB 来源 |
|------|---------|---------|
| tables | `Base.metadata.tables.keys()` | `inspector.get_table_names()` |
| columns | `orm_table.columns` | `inspector.get_columns(table)` |
| column type | `str(orm_col.type)` | `db_col["type"]` |
| nullable | `orm_col.nullable` | `db_col["nullable"]` |
| default | `orm_col.default` | `db_col["default"]` |
| indexes | `orm_table.indexes` | `inspector.get_indexes(table)` |
| unique constraints | `orm_table.constraints` | `inspector.get_unique_constraints(table)` |
| foreign keys | `orm_table.foreign_keys` | `inspector.get_foreign_keys(table)` |
| check constraints | `orm_table.constraints` | `inspector.get_check_constraints(table)` |
| triggers（SQLite） | — | `SELECT name FROM sqlite_master WHERE type='trigger'` |
| FTS 虚拟表 | — | `SELECT name FROM sqlite_master WHERE sql LIKE '%FTS%'` |

退出码：有差异返回 1（CI 友好），无差异返回 0。

**Step 5 — 生产环境移除 create_all()**

- `init_db.py:238` 的 `Base.metadata.create_all()` 改为只在 `settings.ENV == "test"` 时调用
- 生产部署完全依赖 `alembic upgrade head`
- `entrypoint.sh` 已经在 v2.2 改为 `alembic upgrade head` + `python -m app.cli seed`，保留

**Step 6 — 验收（替换 v2.2 P0 验收）**

- [ ] 空库 `alembic downgrade base` 后 `alembic upgrade head` 成功
- [ ] 已有库执行 `diff_schema --full` 报告完全干净（exit 0）
- [ ] 已有库 stamp 到 `0001_root` 后 `alembic current` 输出正确
- [ ] 生产 `init_db.py` 不再调用 `create_all()`（`grep create_all` 无命中）
- [ ] 旧 3 个 revision 在 `_archive/` 下，不在版本链上
- [ ] 数据库行数与迁移前一致（`SELECT count(*) FROM posts/users/comments`）
- [ ] `PRAGMA foreign_key_check` 返回空

---

## 修订 2：P1.5 refresh_token 改两阶段迁移（替换 v2.2 §3.2）

### 三次审核指出的风险

`batch_alter_table(recreate="always")` 在 SQLite 下：
1. 复制整张 users 表 → 写锁 + 磁盘开销
2. 删旧 users 表 → 若 `PRAGMA foreign_keys=ON` 且 `comments.user_id` 外键指向 `users.id`，**删除会失败**
3. Alembic 通常重建表内索引/约束，但**外部触发器、视图、特殊索引需要单独确认**

### v2.3 方案：**两阶段迁移**

#### 阶段 1：新增字段（Migration p1a，主版本部署）

```python
# p1a_add_refresh_token_hash.py
def upgrade():
    # 只新增 nullable 字段，不删旧的
    op.add_column("users", sa.Column("refresh_token_hash", sa.String(64), nullable=True))
    op.create_index("ix_users_refresh_token_hash", "users", ["refresh_token_hash"])

def downgrade():
    op.drop_index("ix_users_refresh_token_hash", table_name="users")
    op.drop_column("users", "refresh_token_hash")
```

**部署阶段 1 的代码改动**：
- `auth.py` 登录/刷新接口：**双写**——同时更新 `refresh_token`（旧）和 `refresh_token_hash`（新）
- `auth.py` token 校验：**双读**——先查 hash，再 fallback 查明文（兼容期）
- 启动一次性脚本 `python -m app.cli migrate_refresh_tokens`：把现有 `refresh_token` 转成 hash 写入新字段，然后清空旧的明文

```python
# app/cli.py
@cli.command()
def migrate_refresh_tokens():
    """一次性把 refresh_token 明文转 hash"""
    import hashlib
    with SessionLocal() as db:
        users = db.query(User).filter(User.refresh_token.isnot(None)).all()
        for u in users:
            if u.refresh_token:
                u.refresh_token_hash = hashlib.sha256(u.refresh_token.encode()).hexdigest()
                u.refresh_token = None  # 清空明文
        db.commit()
```

**阶段 1 验收**：
- [ ] users 表同时存在 `refresh_token`（NULL）和 `refresh_token_hash`（VARCHAR(64)）
- [ ] 所有用户 `refresh_token` 字段为 NULL
- [ ] 所有用户 `refresh_token_hash` 是 64 字符哈希或 NULL
- [ ] 登录/刷新 token 接口测试通过
- [ ] `PRAGMA foreign_key_check` 返回空

#### 阶段 2：删除旧字段（Migration p1b，**下一个维护窗口**）

只在阶段 1 稳定运行至少 1 周后才执行：

```python
# p1b_drop_refresh_token.py
def upgrade():
    # SQLite 不支持 DROP COLUMN < 3.35，仍需 batch_alter_table
    # 但不指定 recreate="always"，让 Alembic 自动判断
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("refresh_token")

def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("refresh_token", sa.String(500), nullable=True))
```

**阶段 2 风险评估**：
- 此时 `refresh_token` 字段已无引用，删除安全性高
- 即使重建表，也不会丢失数据（旧字段已空）
- 但仍需在执行前：
  - 真实数据库备份
  - 恢复演练
  - `PRAGMA foreign_key_check` 校验
  - 行数校验（迁移前后 users 行数一致）
  - 索引/FK/触发器校验

**阶段 2 验收**：
- [ ] users 表只有 `refresh_token_hash`，没有 `refresh_token`
- [ ] users 行数与迁移前一致
- [ ] `comments.user_id` 外键仍指向 `users.id`
- [ ] `SELECT * FROM pragma_index_list('users')` 输出与迁移前一致
- [ ] 登录/刷新 token 接口测试通过

### 与 v2.2 的对比

| 项 | v2.2 | v2.3 |
|----|------|------|
| 迁移次数 | 1 次重建 | 2 次小迁移（间隔 1 周+） |
| 字段重命名 | 一次完成 | 新增 → 双写 → 清空 → 删除 |
| 外键风险 | 高（删旧表可能失败） | 低（不删表，只 add/drop column） |
| 回滚能力 | 一次回滚即恢复 token | 阶段 1 可回滚，阶段 2 回滚需数据补救 |
| 上线时间 | 一次部署 | 阶段 1 + 阶段 2 两次部署 |

---

## 修订 3：P4.6.2 Nginx 正则补边界测试（补充 v2.2 §6.2）

### 三次审核的边界矩阵

核实 `app/schemas/post.py:33` 的 slug pattern：`^[a-zA-Z0-9][a-zA-Z0-9\-_]*$`，**确实禁止斜杠**。所以 `~ ^/posts/[^/]+$` 与单段 slug 一致。但需补 4 项验收：

| 请求路径 | 期望行为 |
|----------|----------|
| `/posts` | 返回前端列表页（不匹配正则，走 `location /`） |
| `/posts/example-slug` | 返回带 OG meta 的后端 HTML（匹配正则，proxy 到 backend） |
| `/posts/example/child` | **明确 404，不能静默 SPA** |
| `/posts/example-slug/`（尾斜杠） | 明确是重定向到无尾斜杠 |

### v2.3 补充设计

**A. 后端壳页面接口显式处理 slug 含斜杠**

```python
# app/api/shell.py
@router.get("/posts/{slug:path}", response_class=HTMLResponse)
def post_shell(slug: str, db: DBSession):
    # slug 含 / 时直接 404，不静默返回 SPA
    if "/" in slug:
        raise HTTPException(404, "文章 slug 不允许包含斜杠")

    post = db.query(Post).filter_by(slug=slug, status="published").first()
    if not post:
        # 不存在的 slug 也 404，不返回 SPA shell
        raise HTTPException(404, "文章不存在")
    ...
```

**B. Nginx 配置加 301 重定向尾斜杠**

```nginx
# /posts/{slug}/ → /posts/{slug}，统一规范化
location ~ ^/posts/([^/]+)/$ {
    return 301 /posts/$1;
}

# /posts/{slug}（无尾斜杠）→ 后端壳
location ~ ^/posts/([^/]+)$ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache post_shell_cache;
    proxy_cache_valid 200 30s;
    proxy_cache_valid 404 10s;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}

# /posts（列表页）→ 前端
location = /posts {
    try_files $uri /index.html;
}

# /posts/ → 301 重定向到 /posts
location = /posts/ {
    return 301 /posts;
}
```

**C. 验收清单（替换 v2.2 P4.6.2 验收）**

- [ ] `curl -I https://domain/posts` → 200，返回 SPA index.html
- [ ] `curl -I https://domain/posts/` → 301，Location: `/posts`
- [ ] `curl -A "Twitterbot" https://domain/posts/example-slug` → 200，HTML 含 `og:title` / `og:image`
- [ ] `curl -I https://domain/posts/example-slug/` → 301，Location: `/posts/example-slug`
- [ ] `curl -I https://domain/posts/example/child` → 404（不是 200 SPA）
- [ ] `curl -I https://domain/posts/不存在-slug` → 404（不是 200 SPA）
- [ ] 浏览器实际访问 `/posts/example-slug`：SPA 挂载正常，meta 标签被前端接管清理（避免重复）
- [ ] `proxy_cache` 命中：第二次访问相同 slug 响应头出现 `X-Cache: HIT`

**D. 未来扩展约束（写进 README）**

若未来支持层级 slug（`/posts/2024/my-post`），需要同步修改：
- FastAPI 路由 `@router.get("/posts/{slug:path}")`
- slug 校验 schema 放宽
- Nginx 正则改 `~ ^/posts/(.+)$`
- canonical URL 生成
- proxy_cache key 不变
- SEO sitemap 与壳页面 OG 逻辑同步

---

## v2.3 工时调整

P0 真实 baseline 重写工作量增加：
- 写 `0001_root_baseline.py` 全表定义：1 天
- `diff_schema --full` 全方位对比：0.5 天
- 已有库迁移演练 + 备份恢复测试：0.5 天

P1.5 改两阶段迁移工时分散但总量略增：
- 阶段 1 + migrate_refresh_tokens CLI：0.5 天
- 阶段 1 观察期（不计入开发时间）
- 阶段 2：0.3 天

P4.6.2 边界处理：+0.3 天

**v2.3 总工时：23-32 天**（v2.2 的 22-30 天再上浮 1 天）。

---

## 三次审核响应小结

| 审核点 | v2.2 状态 | v2.3 处理 |
|--------|----------|----------|
| P0.2.1 | NO-GO（baseline 仍会先跑旧迁移） | **重建迁移链**：归档旧 revision + 新 `0001_root` 起点 + 已有库必须 `diff_schema --full` 干净才能 stamp |
| P1.5 | Conditional GO（重建表风险高） | **两阶段迁移**：阶段 1 新增字段 + 双写 + migrate CLI；阶段 2 删除旧字段（间隔 1 周+） |
| P4.6.2 | 可行但需补边界 | **4 项验收 + 301 重定向尾斜杠 + 404 显式拒绝含斜杠 slug + 未来扩展约束写入 README** |

---

## 变更历史（v2.3 追加）

- **v2.3** (2026-07-25 23:11) — 三次审核修订，3 项：
  1. Alembic 迁移链完全重建（归档旧 revision + 0001_root 新起点 + diff_schema 全方位对比）
  2. refresh_token 改两阶段迁移（add_column → 双写 → migrate CLI → 间隔期 → drop_column）
  3. Nginx `/posts/{slug}` 加 301 尾斜杠重定向 + 404 含斜杠拒绝 + 8 项边界验收

工时校准 22-30 → 23-32 天。

---

_文档 v2.3 · 2026-07-25 23:11_
_下一步：等待用户确认 v2.3 通过后进入 P0 执行。_
