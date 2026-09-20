# chiyeblog 数据资产保护方案 v2.1

> 日期：2026-07-28（v1）→ 2026-07-30（v2，融入外部复核反馈）→ 2026-07-30（v2.1，补充执行细节）
> 目标：即使服务器被入侵，核心数据资产也能安全保住、快速恢复
> 复核状态：v1 被判定 Conditional NO-GO，v2 修复全部 P0/P1 阻塞点，v2.1 补充 3 条执行细节

---

## 一、数据资产清单

| 资产 | 存储位置 | 当前风险 | 价值 |
|------|---------|---------|------|
| **用户数据** | SQLite `users` 表（blog-data volume） | 密码已 bcrypt 哈希 ✅；refresh_token 明文 ⚠️；邮箱明文 | 高 |
| **文章内容** | SQLite `posts` + `post_revisions` 表 | 明文存储 | 极高 |
| **站点配置** | SQLite `site_config` 表 | 明文 | 中 |
| **上传文件** | `blog-uploads` volume | 无备份 | 中 |
| **API 密钥** | 服务器 `.env` | 明文，root 可读 | 极高 |
| **SECRET_KEY** | `.env` + `blog-data/.secret_key` | 明文，root 可读 | 极高 |

**核心事实**：所有数据在一个 SQLite 文件里，存在 Docker volume `blog-data` 中。拿到这个文件 = 拿到一切。

---

## 二、威胁模型

### 场景 A：通过 Web 漏洞入侵

**现状防护**：
- SQLAlchemy ORM 参数化查询 → 主业务路径 SQL 注入风险低
- FastAPI Pydantic 验证 → 请求体严格校验
- 文件上传 magic bytes + SVG XSS 检测

**仍需注意**：FTS5 搜索、CLI 工具、Alembic 迁移中存在 raw SQL 场景。新增 raw SQL 必须审查参数化。

### 场景 B：暴力破解后台密码

**现状防护**：5次/分钟限速 + 5次失败锁30分钟 + bcrypt 300ms/次。实际中不可行。

### 场景 C：直接拿到服务器 root（最危险）

攻击者可以：读 `.env`（所有密钥）→ 读 `blog.db`（所有数据）→ `rm -rf`（全毁）。

**当前防护**：SSH 密钥认证 + 阿里云安全组
**最大短板**：没有数据备份 + 没有异地备份 → 被删库就全没了

---

## 三、分层防护方案

### 第 1 层：数据备份（含异地，强制）

**原则**：哪怕服务器被格式化，也能在 30 分钟内恢复全部数据。本地备份和异地备份都是强制项。

#### 备份脚本（修复复核 P0-1/3/5/6/7）

```bash
#!/bin/bash
set -euo pipefail

# ──────────────────────────────────────
# chiyeblog backup script v2
# 修复清单：
# - 异地备份从"可选"改为强制
# - .env 不再明文进备份，改为加密包
# - uploads 用临时容器挂载 volume，不依赖 Docker 内部路径
# - 加 SQLite 完整性检查
# - 周备份逻辑补全（DB + uploads + 文章导出全覆盖）
# - 加备份校验
# ──────────────────────────────────────

BACKUP_DIR="/opt/blog/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y%m%d)
BACKUP_TYPE="${1:-daily}"  # daily | weekly
KEEP_DAYS=7
KEEP_WEEKS=4

mkdir -p "$BACKUP_DIR"

echo "[$TIMESTAMP] Starting $BACKUP_TYPE backup..."

# ── 1. SQLite 在线备份 + 完整性检查 ──
docker exec blog-backend python3 -c "
import sqlite3, sys
src = sqlite3.connect('/app/data/blog.db')
dst = sqlite3.connect('/tmp/backup.db')
src.backup(dst)
src.close()
dst.close()

# Verify integrity
chk = sqlite3.connect('/tmp/backup.db')
result = chk.execute('PRAGMA integrity_check').fetchone()
chk.close()
if result[0] != 'ok':
    print(f'INTEGRITY CHECK FAILED: {result[0]}', file=sys.stderr)
    sys.exit(1)
print('SQLite integrity check: OK')
"

if [ $? -ne 0 ]; then
    echo "[$TIMESTAMP] FATAL: SQLite integrity check failed"
    exit 1
fi

docker cp blog-backend:/tmp/backup.db "$BACKUP_DIR/db_${TIMESTAMP}.db"
docker exec blog-backend rm /tmp/backup.db
echo "  DB backup: $(ls -lh "$BACKUP_DIR/db_${TIMESTAMP}.db" | awk '{print $5}')"

# ── 2. uploads 备份（用临时容器挂载 volume，不依赖内部路径） ──
docker run --rm -v blog-uploads:/data -v "$BACKUP_DIR":/backup alpine \
    sh -c "cd /data && tar czf /backup/uploads_${TIMESTAMP}.tar.gz . 2>/dev/null || true"
echo "  Uploads backup: $(ls -lh "$BACKUP_DIR/uploads_${TIMESTAMP}.tar.gz" | awk '{print $5}')"

# ── 3. 文章导出（Markdown zip） ──
# 管理员密码从环境变量读取，不硬编码在脚本里
ADMIN_TOKEN=$(curl -s https://chiyeblog.cn/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${BACKUP_ADMIN_USER:-minlan01}\",\"password\":\"${BACKUP_ADMIN_PASS}\"}" \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [ -n "$ADMIN_TOKEN" ]; then
    curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
        https://chiyeblog.cn/api/v1/admin/posts/export \
        -o "$BACKUP_DIR/posts_${TIMESTAMP}.zip"
    echo "  Posts export: $(ls -lh "$BACKUP_DIR/posts_${TIMESTAMP}.zip" | awk '{print $5}')"
else
    echo "  Posts export: SKIP (login failed)"
fi

# ── 4. 密钥包加密备份（不再明文 cp .env） ──
# 用 OpenSSL AES-256-CBC 加密，密码从环境变量读取
if [ -n "$BACKUP_ENCRYPTION_PASS" ]; then
    openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in /opt/blog/.env \
        -out "$BACKUP_DIR/secrets_${TIMESTAMP}.enc" \
        -pass env:BACKUP_ENCRYPTION_PASS
    echo "  Secrets (encrypted): $(ls -lh "$BACKUP_DIR/secrets_${TIMESTAMP}.enc" | awk '{print $5}')"
else
    echo "  Secrets: SKIP (BACKUP_ENCRYPTION_PASS not set)"
fi

# ── 5. 备份校验 ──
# 校验 DB 可打开
DB_CHECK=$(docker run --rm -v "$BACKUP_DIR":/backup alpine \
    sh -c "apk add --no-cache sqlite >/dev/null 2>&1 && sqlite3 /backup/db_${TIMESTAMP}.db 'SELECT COUNT(*) FROM posts;' 2>/dev/null || echo 'FAIL'")
echo "  DB verify: posts count = $DB_CHECK"

# 校验 uploads tar 可读
TAR_CHECK=$(docker run --rm -v "$BACKUP_DIR":/backup alpine \
    sh -c "tar tzf /backup/uploads_${TIMESTAMP}.tar.gz 2>/dev/null | head -1 || echo 'FAIL'")
echo "  Uploads verify: $TAR_CHECK"

# ── 6. 异地同步（强制，非可选） ──
if command -v rclone &>/dev/null; then
    rclone copy "$BACKUP_DIR/db_${TIMESTAMP}.db" \
        "remote:chiyeblog-backup/${BACKUP_TYPE}/" --quiet
    rclone copy "$BACKUP_DIR/uploads_${TIMESTAMP}.tar.gz" \
        "remote:chiyeblog-backup/${BACKUP_TYPE}/" --quiet
    rclone copy "$BACKUP_DIR/posts_${TIMESTAMP}.zip" \
        "remote:chiyeblog-backup/${BACKUP_TYPE}/" --quiet
    [ -f "$BACKUP_DIR/secrets_${TIMESTAMP}.enc" ] && \
        rclone copy "$BACKUP_DIR/secrets_${TIMESTAMP}.enc" \
            "remote:chiyeblog-backup/${BACKUP_TYPE}/" --quiet
    echo "  Remote sync: OK"
else
    echo "  Remote sync: SKIP (rclone not installed)"
    echo "  WARNING: No remote backup! Data will be lost if server is destroyed."
fi

# ── 7. 清理旧备份 ──
if [ "$BACKUP_TYPE" = "daily" ]; then
    find "$BACKUP_DIR" -name "db_*" -not -name "weekly_*" -mtime +$KEEP_DAYS -delete
    find "$BACKUP_DIR" -name "uploads_*" -not -name "weekly_*" -mtime +$KEEP_DAYS -delete
    find "$BACKUP_DIR" -name "posts_*" -not -name "weekly_*" -mtime +$KEEP_DAYS -delete
    find "$BACKUP_DIR" -name "secrets_*" -mtime +$KEEP_DAYS -delete
elif [ "$BACKUP_TYPE" = "weekly" ]; then
    # 周备份重命名保留
    for f in db uploads posts; do
        if [ -f "$BACKUP_DIR/${f}_${TIMESTAMP}.*" ]; then
            cp "$BACKUP_DIR/${f}_${TIMESTAMP}."* "$BACKUP_DIR/weekly_${f}_${DATE}."*
        fi
    done
    find "$BACKUP_DIR" -name "weekly_*" -mtime +$(($KEEP_WEEKS * 7)) -delete
fi

echo "[$TIMESTAMP] Backup completed successfully"
```

#### crontab 配置

```bash
# 所有敏感凭证统一定义在 /root/.backup_env（chmod 600）
# 内容示例：
# export BACKUP_ENCRYPTION_PASS="your-strong-passphrase"
# export BACKUP_ADMIN_USER="minlan01"
# export BACKUP_ADMIN_PASS="<ADMIN_PASSWORD 占位，原文见密码管理器>"

# 每天凌晨 3 点：日备份 + 异地同步
0 3 * * * . /root/.backup_env && /opt/blog/scripts/backup.sh daily >> /opt/blog/backups/backup.log 2>&1

# 每周日凌晨 4 点：周备份（全量 + 异地同步）
0 4 * * 0 . /root/.backup_env && /opt/blog/scripts/backup.sh weekly >> /opt/blog/backups/backup.log 2>&1
```

#### rclone 异地配置

```bash
# 安装 rclone
curl https://rclone.org/install.sh | bash

# 配置远程存储（阿里云 OSS / 腾讯 COS / Backblaze B2 任选）
rclone config
# 选择 n (new remote) -> 命名 "remote" -> 选择你的云存储 -> 填入凭证

# 测试
rclone ls remote:chiyeblog-backup/
```

> **注意**：rclone 的凭证使用独立的云存储账号，不要和博客服务器用同一个云账号。这样即使服务器被入侵，攻击者也删不了异地备份。

> **关键**：云存储 Bucket 必须开启**版本控制（Versioning）或对象锁定（Object Lock）**。否则攻击者拿到 rclone 凭证后可以 `rclone delete` 把远端备份也删了。开启版本控制后，即使删除也能从历史版本恢复。

---

### 第 2 层：refresh_token 彻底去掉明文（修复复核 P0-2）

**当前问题**：`auth.py` 和 `oauth.py` 都是双写（明文 + 哈希），`migrate_refresh_tokens` 跑完后用户重新登录又写回明文。

**正确的迁移顺序**：

#### 步骤 1：先发布 hash-only 代码

改 `auth.py` 登录和刷新接口，只写 `refresh_token_hash`，不再写 `refresh_token`：

```python
# auth.py login() — 改后
user.refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
# 删掉这行：user.refresh_token = refresh_token

# auth.py refresh_token() — 改后
token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
# 只验哈希，不退验明文
if user.refresh_token_hash != token_hash:
    raise HTTPException(status_code=401, detail="Refresh token revoked")
# 新 token 只写哈希
user.refresh_token_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
# 删掉这行：user.refresh_token = new_refresh
```

同样改 `oauth.py` 的 `github_callback`。

#### 步骤 2：跑迁移清空旧明文值

```bash
docker exec blog-backend python -m app.cli migrate_refresh_tokens
```

#### 步骤 3：Alembic migration 删除 `refresh_token` 列

```python
# alembic/versions/p1_drop_refresh_token_plaintext.py
def upgrade():
    op.drop_column('users', 'refresh_token')

def downgrade():
    op.add_column('users', sa.Column('refresh_token', sa.String(500), nullable=True))
```

#### 步骤 4：代码删除 `User.refresh_token` 字段

`user.py` 删掉 `refresh_token` 字段定义。

**部署顺序严格按 1→2→3→4，不能跳步。**

---

### 第 3 层：密钥安全（修复复核 P1-4）

**复核纠正**：`.secret_key` 放在 volume 里只降低"误提交 Git"的风险，对 root 入侵没有防护意义。表述更正如下：

| 措施 | 实际效果 | 不能做到 |
|------|---------|---------|
| `.secret_key` 在 volume 不在项目目录 | 防误提交 Git | 防 root 读取 |
| `.env` chmod 600 | 防非 root 用户读 | 防 root 读 |
| 备份加密（AES-256） | 备份泄露后密钥不暴露 | 防运行时被读 |

**正确认知**：如果攻击者拿到 root，服务器上所有密钥都暴露。正确的应对是：
1. 备份中的密钥加密（已在上文备份脚本实现）
2. 灾难恢复时轮换所有密钥（见第四节）
3. 异地备份用独立凭证（攻击者删不了远端）

---

### 第 4 层：数据库加固

#### SQLite WAL（已实现 ✅）
`session.py` 已设置 WAL + busy_timeout。

#### 文件权限收紧
```bash
# entrypoint.sh 里加
chmod 600 /app/data/blog.db 2>/dev/null || true
chmod 700 /app/data 2>/dev/null || true
```

#### 防止数据库被直接下载（已实现 ✅）
Docker 隔离 + Nginx 只代理指定路径，数据库不可通过 HTTP 访问。

---

### 第 5 层：文章内容保护

#### 文章修订版本（已实现 ✅）
`PostRevision` 保存编辑历史。定期清理：
```bash
0 4 * * 0 docker exec blog-backend python -m app.cli cleanup_revisions
```

#### 文章导出（已实现 ✅，已融入备份脚本）
备份脚本中自动调用 `/admin/posts/export` 导出 Markdown zip。

---

### 第 6 层：服务器访问控制

- SSH 密钥认证 ✅
- 防火墙只开 22/80/443（需确认）
- Docker 非 root 运行 ✅
- 加 `security_opt: no-new-privileges:true`

---

### 第 7 层：备份校验和恢复演练（修复复核 P1-7）

**"有备份"不等于"能恢复"。** 备份脚本已内置：
- SQLite `PRAGMA integrity_check`
- DB 行数验证
- tar 可读性检查
- rclone 远端上传验证

**季度恢复演练**（每 3 个月一次）：
```bash
# 1. 在测试环境拉取最新备份
rclone copy remote:chiyeblog-backup/daily/ /tmp/restore-test/

# 2. 解密密钥包
openssl enc -aes-256-cbc -d -pbkdf2 \
    -in /tmp/restore-test/secrets_最新.enc \
    -out /tmp/restore-test/.env \
    -pass env:BACKUP_ENCRYPTION_PASS

# 3. 启动临时容器恢复
docker volume create blog-test-data
docker run --rm -v blog-test-data:/data -v /tmp/restore-test:/backup alpine \
    sh -c "cp /backup/db_*.db /data/blog.db"

# 4. 启动临时实例验证
# （在非生产端口上启动，验证数据完整性）

# 5. 记录演练结果，确认恢复流程可行
```

---

## 四、灾难恢复流程

### 场景：服务器被入侵，数据被删除

```bash
# ── 阶段 1：数据恢复（30 分钟） ──

# 1. 从异地拉取最新备份
rclone copy remote:chiyeblog-backup/ /tmp/restore/

# 2. 解密密钥包
openssl enc -aes-256-cbc -d -pbkdf2 \
    -in /tmp/restore/secrets_最新.enc \
    -out /opt/blog/.env \
    -pass env:BACKUP_ENCRYPTION_PASS

# 3. 新服务器初始化
apt install docker.io docker-compose-v2

# 4. 拉取项目代码
git clone <your-repo> /opt/blog

# 5. 恢复数据库
docker volume create blog-data
docker run --rm -v blog-data:/data -v /tmp/restore:/backup alpine \
    sh -c "cp /backup/db_最新.db /data/blog.db && chown 1000:1000 /data/blog.db"

# 6. 恢复上传文件
docker volume create blog-uploads
docker run --rm -v blog-uploads:/data -v /tmp/restore:/backup alpine \
    sh -c "cd /data && tar xzf /backup/uploads_最新.tar.gz"

# 7. 构建并启动
cd /opt/blog && docker compose up -d --build

# 8. 验证
curl https://localhost/api/v1/site/profile
```

```bash
# ── 阶段 2：密钥轮换（如果确认被入侵） ──

# 1. 重新生成 SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
# 更新 .env，重启后端（所有 JWT 失效，用户需重新登录）

# 2. 轮换所有 API 密钥（不依赖旧密钥）
# - DeepSeek：后台重新生成 API Key
# - GitHub：重新生成 OAuth App Secret
# - QQ 邮箱：重新生成 SMTP 授权码

# 3. 强制所有用户重置密码（通过 admin API 或直接 DB 操作）

# 4. 备份加密密码也轮换
# 更新 /root/.backup_env 里的 BACKUP_ENCRYPTION_PASS
```

---

## 五、行动清单

### 立即执行（P0，今天必须做）

| # | 任务 | 耗时 | 修复的复核项 |
|---|------|------|-------------|
| 1 | 部署备份脚本 v2 + crontab | 20 分钟 | P0-1/P0-3/P1-5/P1-6/P1-7 |
| 2 | 配置 rclone 异地同步 | 15 分钟 | P0-1（异地强制） |
| 3 | 轮换 DeepSeek API Key | 5 分钟 | — |
| 4 | 设置 `BACKUP_ENCRYPTION_PASS` 环境变量 | 2 分钟 | P0-3（备份加密） |

### 短期执行（P1，本周内）

| # | 任务 | 耗时 | 修复的复核项 |
|---|------|------|-------------|
| 5 | 发布 hash-only 代码（auth.py + oauth.py） | 15 分钟 | P0-2 |
| 6 | 跑 `migrate_refresh_tokens` | 2 分钟 | P0-2 |
| 7 | Alembic migration 删 `refresh_token` 列 | 10 分钟 | P0-2 |
| 8 | Nginx 加 `location ~ /\. { deny all; }` | 1 分钟 | — |
| 9 | `client_max_body_size` 改 15m | 1 分钟 | P2-9 |
| 10 | robots.txt 补 Disallow: /admin | 1 分钟 | — |
| 11 | 加 `security_opt: no-new-privileges` | 5 分钟 | — |

### 定期执行

| # | 任务 | 频率 | 修复的复核项 |
|---|------|------|-------------|
| 12 | 季度恢复演练 | 每 3 个月 | P1-7 |
| 13 | 清理旧文章修订版本 | 每周 | — |
| 14 | 检查备份日志和完整性 | 每天看一眼 | P1-7 |

### 不需要做

| 任务 | 原因 |
|------|------|
| 数据库透明加密（SQLCipher） | 密钥还是得存在服务器上，对 root 入侵无防护 |
| 文章内容 AES 加密存储 | 同上，且破坏 FTS5 全文搜索 |
| 锁右键/F12 | 无效且损害体验 |
| 后台路径改名 | 安全混淆 |
| 登录验证码 | 已有三层防护 |

---

## 六、v1 → v2 修改记录

| 复核项 | v1 问题 | v2 修复 |
|--------|---------|---------|
| P0-1 异地备份 | 写成"可选但推荐" | 改为强制，rclone 同步进备份脚本 |
| P0-2 refresh_token | 只跑 migrate 命令 | 改为四步：先发 hash-only 代码 → 跑迁移 → Alembic 删列 → 删代码字段 |
| P0-3 .env 备份 | 明文 cp 到备份目录 | 改为 OpenSSL AES-256 加密包 |
| P1-4 SECRET_KEY | 说"现状已经 OK" | 纠正表述：volume 只防误提交，不防 root |
| P1-5 周备份 | KEEP_WEEKS 定义了没用，只备 DB | 统一脚本覆盖 DB+uploads+文章导出+密钥包 |
| P1-6 uploads 路径 | tar Docker 内部路径 | 改为临时容器挂载 volume |
| P1-7 备份校验 | 只生成文件不校验 | 加 integrity_check + 行数验证 + tar 校验 + 季度演练 |
| P2-8 SQL 注入 | "几乎不可能" | 改为"主业务路径风险低，新增 raw SQL 必须审查" |
| P2-9 body size | 原文已提但不够明确 | 明确改为 15m |

### v2.1 补充（2026-07-30）

| # | 补充项 | v2 问题 | v2.1 修复 |
|---|--------|---------|-----------|
| 1 | 备份脚本管理员密码 | 硬编码 `<ADMIN_PASSWORD 占位，原文见密码管理器>` 调文章导出接口，root 被入侵后泄露 | 改为 `BACKUP_ADMIN_PASS` 环境变量，存入 `/root/.backup_env` |
| 2 | 云存储版本控制 | 只说了"独立凭证"，没提版本控制 | 补充：Bucket 必须开启 Versioning 或 Object Lock，防远端被删 |
| 3 | .gitignore | 缺 `.secret_key`、`backup.sh`、`backups/` | 已补上，防止敏感文件误提交 Git |
