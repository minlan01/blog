# chiyeblog 安全审计报告

> 审计日期：2026-07-28
> 基于源码：当前工作树 + 服务器实际部署版本（8.137.18.28 / chiyeblog.cn）
> 架构：Caddy (HTTPS) → Nginx (前端) → FastAPI/Gunicorn (后端) → SQLite

---

## 一、测评意见逐条评估

### 1. 敏感目录防护 ✅ 采纳（需小幅调整）

**测评意见**：禁止访问 caches、uploadfile、log、config，避免全局 777

**结合源码的实际情况**：

| 目录 | 当前架构 | 外部可访问？ | 需要处理？ |
|------|---------|-------------|-----------|
| `config`（`.env`） | 在宿主机 `/opt/blog/.env`，容器内通过环境变量注入 | ❌ 不可访问 | 已隔离，不需要 |
| `log` | Gunicorn 日志输出到 stdout，docker logs 查看 | ❌ 不可访问 | 已隔离，不需要 |
| `uploads/` | Docker volume `blog-uploads`，通过 `/upload/{id}` 端点受控访问 | ⚠️ 需确认 | 见下方 |
| `__pycache__` | Python 字节码在容器镜像内 | ❌ 不可访问 | 已隔离 |

**结论**：你的 Docker 三层架构已经天然隔离了敏感目录——外部请求经过 Caddy → Nginx → FastAPI，只有 `/api/`、`/uploads/{id}`、`/health`、`/assets/` 四条路径通向外网，其余全部 404。不存在"全局 777"的问题（容器内 `appuser` 非 root 运行，`.env` 不在容器内）。

**实际需要做的**：在 Nginx 加一条规则拦截隐藏文件和 `.env`（防御性措施，即使当前架构已经隔离）：

```nginx
# 在 nginx.conf 的 server 块内加：
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
}
```

**`.htaccess` 不适用**：你用的是 Nginx 不是 Apache，`.htaccess` 是 Apache 专有机制。

---

### 2. 登录验证码 ⚠️ 不推荐优先做

**测评意见**：登录加入动态验证码防止密码爆破

**结合源码的实际情况**：

你的 `auth.py` 已经实现了三层暴力破解防护：

```
1. slowapi 限速：5次/分钟（@limiter.limit("5/minute")）
2. 账号锁定：连续失败 5 次锁 30 分钟（MAX_FAILED_ATTEMPTS=5, LOCK_DURATION_MINUTES=30）
3. bcrypt 哈希：每次验证约 300ms，暴力破解不现实
```

**验证码的投入产出比分析**：

- 现有防护已经让暴力破解在实际中不可行（5次/分钟 + 锁定 30 分钟 + bcrypt 慢哈希）
- 图形验证码会损害用户体验（每次登录都要输验证码）
- 如果一定要加，推荐用 hCaptcha（无感验证，不影响正常用户），不推荐自研图形验证码

**结论**：已有防护足够，验证码优先级低。如果未来有被攻击迹象再考虑加 hCaptcha。

---

### 3. 后台路径改名 ❌ 不推荐

**测评意见**：不直接使用 /admin，改为伪静态路径

**为什么这是安全混淆（Security through Obscurity）**：

- 你的后台安全靠的是 `SuperAdmin` 依赖（`deps.py:60-64`），不是路径隐藏
- 攻击者扫后台用的是目录爆破工具（dirsearch/gobuster），会扫 `/admin`、`/manage`、`/dashboard`、`/backend` 等上千个常见路径，改名挡不住
- 改名后维护成本高：前端路由、nginx 配置、书签、历史链接全要跟着改
- 反而可能漏掉某个旧路径的权限检查，制造新的安全问题

**实际应该做的**（已有 + 补充）：

```diff
# robots.txt（已有，补一行）
User-agent: *
Allow: /
+ Disallow: /admin
Sitemap: /api/v1/sitemap.xml
```

这样搜索引擎不会索引后台页面，够了。真正的防护是权限验证，不是路径隐藏。

---

### 4. root 文件（robots.txt） ✅ 已有，补充优化

**测评意见**：需要 root 文件防止浏览器抓取

**结合源码**：

`frontend/public/robots.txt` 当前内容：
```
User-agent: *
Allow: /
Sitemap: /api/v1/sitemap.xml
```

**需要补充的**：
1. `Disallow: /admin` — 防止搜索引擎索引后台
2. `Sitemap` 改为绝对 URL — 当前是相对路径，部分爬虫不支持

优化后：
```
User-agent: *
Allow: /
Disallow: /admin

Sitemap: https://chiyeblog.cn/api/v1/sitemap.xml
```

---

### 5. 锁右键、锁 F12 ❌ 强烈反对

**测评意见**：页面锁右键，锁 F12

**为什么不应该做**：

| 问题 | 说明 |
|------|------|
| 挡不住任何人 | 打开 DevTools 有 10+ 种方式：浏览器菜单、Ctrl+Shift+I、Ctrl+Shift+J、Ctrl+U 查看源码、Fiddler 抓包等 |
| 伤害正常用户 | 读者想复制文字、开发者想看排版、手机用户想保存图片——全被恶心到 |
| 损害 SEO | 搜索引擎爬虫遇到 JS 阻断可能降低排名 |
| 显得不专业 | 2026 年锁右键/F12 是外行做法，降低博客的技术形象 |
| 无法隐藏前端代码 | 浏览器的本质就是下载 HTML/JS/CSS 在本地渲染，无法对用户隐藏 |

**你的前端代码已经有的保护**：
- Vue 组件编译后是混淆压缩的（vite build 产出 `index-xxx.js`，变量名全部混淆）
- 真正敏感的逻辑（密码哈希、用户验证、数据库操作）全在后端，前端看不到
- API 有 JWT 认证 + 权限分层，看得到接口地址也调不了

**结论**：不要锁。如果你担心的是别人抄博客主题/样式，可以在页脚加 CC 协议声明，比锁右键有效 100 倍。

---

## 二、源码审计发现的真实安全问题

以下是在审查源码过程中发现的、测评意见**没提到但确实存在**的问题，按优先级排序：

### P0：本地 .env 泄露真实 DeepSeek API Key（上线前必修）

**文件**：`D:\blog\.env` 第 7 行
```
DEEPSEEK_API_KEY=sk-***已脱敏，原文见本地 .env***
```

**问题**：这是真实的 API Key，如果项目仓库公开或 `.env` 被意外提交到 Git，密钥会泄露。

**修复**：
1. 去 DeepSeek 后台轮换（重新生成）API Key
2. 本地 `.env` 的 key 改为空或占位符
3. 确保 `.gitignore` 包含 `.env`
4. 服务器上的 `.env` 填入新 key（当前为空，需要时再填）

### P1：CSP 缺少 connect-src 的 HTTPS 来源

**文件**：`frontend/nginx.conf` 第 19 行

当前 CSP：
```
connect-src 'self';
```

**问题**：如果前端需要请求外部 API（如字体加载、第三方分析），会被 CSP 拦截。当前不影响功能，但如果未来加功能可能踩坑。

**建议**：按需扩展，目前不需要改。

### P2：client_max_body_size 过大

**文件**：`frontend/nginx.conf` 第 21 行

```nginx
client_max_body_size 1024m;
```

**问题**：后端 `MAX_UPLOAD_SIZE_MB=10`，但 Nginx 允许 1024MB 上传。攻击者可以发大文件消耗带宽。

**建议**：改为 `client_max_body_size 15m;`（略大于后端限制，留余量给 multipart 封装）。

### P2：Caddy HSTS 头缺少 preload

**文件**：服务器 `/opt/blog/Caddyfile`

当前：
```
Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

**建议**：加 `preload`（如果未来要提交到 HSTS preload list）：
```
Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

不需要时可以不改，但加上没坏处。

---

## 三、已有安全机制清单

以下是你项目里**已经在工作的安全防护**，测评者可能没注意到：

| 机制 | 实现位置 | 作用 |
|------|---------|------|
| JWT 认证 + 过期 | `security.py:21-36` | access token 30分钟过期，refresh token 30天 |
| bcrypt 密码哈希 | `security.py:13-18` | 每次哈希约 300ms，抗彩虹表 |
| 密码强度校验 | `security.py:81-92` | 8位+大写+小写+数字 |
| 登录限速 | `auth.py:69` | 5次/分钟 |
| 账号锁定 | `auth.py:73-94` | 5次失败锁30分钟 |
| SuperAdmin 权限 | `deps.py:60-64` | 后台操作需 super_admin 角色 |
| must_change_password | `deps.py:50-57` | 初始密码强制修改 |
| CORS 白名单 | `config.py:11` | 只允许指定域名跨域 |
| 文件上传校验 | `upload.py:38-113` | MIME 类型 + magic bytes 双重验证 |
| 图片压缩 | `upload.py:116-168` | 上传图片自动压缩+EXIF 去除 |
| SVG XSS 防护 | `upload.py:60-69` | SVG 文件检测 script/iframe/on* 事件 |
| 非 root 运行 | `Dockerfile:40` | 容器内 `appuser` 用户 |
| server_tokens off | `nginx.conf:6` | 隐藏 Nginx 版本号 |
| X-Frame-Options DENY | `nginx.conf:15` | 防止点击劫持 |
| CSP 策略 | `nginx.conf:19` | 限制脚本/样式/图片来源 |
| HSTS | `Caddyfile` | 强制 HTTPS |
| refresh_token 哈希 | `auth.py:104-105` | refresh_token 逐步从明文存储迁移到 SHA256 哈希 |

---

## 四、推荐行动清单（按优先级）

### 立即执行（10 分钟内）

- [ ] **轮换 DeepSeek API Key**：去 DeepSeek 后台重新生成，旧 key 作废
- [ ] **Nginx 加隐藏文件拦截**：`location ~ /\. { deny all; }`
- [ ] **robots.txt 补 Disallow: /admin + 绝对 URL Sitemap**
- [ ] **client_max_body_size 改为 15m**

### 短期可选（如果需要）

- [ ] Caddy HSTS 加 preload
- [ ] 如果未来有被暴力攻击迹象，再加 hCaptcha

### 不推荐做

- [ ] ~~后台路径改名~~：安全混淆，无效且有维护成本
- [ ] ~~锁右键/F12~~：损害用户体验，无实际效果
- [ ] ~~登录验证码~~：已有三层防护，投入产出比低
- [ ] ~~`.htaccess`~~：Apache 机制，你的架构是 Nginx

---

## 五、总结

测评者的方向整体是对的——关注安全是好事。但其中有几条属于"看起来安全但实际无效"的措施（后台改名、锁右键/F12），不应该花精力做。

真正值得做的是：**Nginx 敏感文件拦截 + client_max_body_size 收紧 + API Key 轮换**，总共 10 分钟。

你的 Docker 架构已经天然隔离了大部分敏感目录（.env 不在容器内、logs 走 stdout、uploads 受控访问），不需要额外处理。已有三层暴力破解防护（限速+锁定+bcrypt），验证码是多余的。
