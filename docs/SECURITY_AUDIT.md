# chiyeblog 安全审计报告

> 审计日期：2026-07-28 · 重写日期：2026-09-20（移除敏感信息后的干净版本）
> 基于源码：当前工作树 + 服务器实际部署版本（www.chiyeblog.cn）
> 架构：Caddy (HTTPS) → Nginx (前端) → FastAPI/Gunicorn (后端) → MySQL + MinIO

> 注：本报告曾引用真实 DeepSeek API Key 作为泄露示例，2026-09-20 重写时删除。
> 涉及凭证的内容一律只写"见本地 .env"，不在仓库中出现原文。

---

## 一、测评意见逐条评估

### 1. 敏感目录防护 ✅ 已采纳并落实

**测评意见**：禁止访问 caches、uploadfile、log、config，避免全局 777

**结合架构的实际情况**：

| 目录 | 当前架构 | 外部可访问？ | 状态 |
|------|---------|-------------|------|
| `config`（`.env`） | 宿主机 `/opt/blog/.env`，容器内通过环境变量注入 | ❌ 不可访问 | 已隔离 |
| `log` | Gunicorn 日志输出到 stdout，docker logs 查看 | ❌ 不可访问 | 已隔离 |
| `uploads/` | 受控端点访问 | ⚠️ 需确认 | 见下方 |
| `__pycache__` | Python 字节码在容器镜像内 | ❌ 不可访问 | 已隔离 |

外部请求经过 Caddy → Nginx → FastAPI，只有 `/api/`、`/upload/{id}`、`/health`、`/assets/`、`/unpkg/` 五条路径通向外网，其余全部 404。容器内以非 root 用户运行。

**已落实**：Nginx 拦截隐藏文件和 `.env`：

```nginx
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
}
```

**`.htaccess` 不适用**：本项目用 Nginx 不是 Apache，`.htaccess` 是 Apache 专有机制。

---

### 2. 登录验证码 ⚠️ 不推荐优先做

**测评意见**：登录加入动态验证码防止密码爆破

已有三层暴力破解防护：

```
1. slowapi 限速：5次/分钟（@limiter.limit("5/minute")）
2. 账号锁定：连续失败 5 次锁 30 分钟（MAX_FAILED_ATTEMPTS=5, LOCK_DURATION_MINUTES=30）
3. bcrypt 哈希：每次验证约 300ms，暴力破解不现实
```

**投入产出比分析**：

- 现有防护已让暴力破解在实际中不可行
- 图形验证码会损害用户体验（每次登录都要输验证码）
- 如果一定要加，推荐用 hCaptcha（无感验证），不推荐自研图形验证码

**结论**：已有防护足够，验证码优先级低。有被攻击迹象再考虑 hCaptcha。

---

### 3. 后台路径改名 ❌ 不推荐

**测评意见**：不直接使用 /admin，改为伪静态路径

这是安全混淆（Security through Obscurity）：

- 后台安全靠的是 `SuperAdmin` 依赖（权限验证），不是路径隐藏
- 攻击者扫后台用目录爆破工具（dirsearch/gobuster），改名挡不住
- 改名后维护成本高：前端路由、nginx 配置、书签、历史链接全要跟着改
- 反而可能漏掉某个旧路径的权限检查，制造新的安全问题

**已落实**：`robots.txt` 已包含 `Disallow: /admin` + 绝对 URL Sitemap，搜索引擎不索引后台。真正的防护是权限验证，不是路径隐藏。

---

### 4. root 文件（robots.txt） ✅ 已完成

当前内容已按建议优化：

```
User-agent: *
Allow: /
Disallow: /admin

Sitemap: https://chiyeblog.cn/api/v1/sitemap.xml
```

---

### 5. 锁右键、锁 F12 ❌ 强烈反对

**测评意见**：页面锁右键，锁 F12

| 问题 | 说明 |
|------|------|
| 挡不住任何人 | 打开 DevTools 有 10+ 种方式：浏览器菜单、快捷键、Ctrl+U 查看源码、抓包工具等 |
| 伤害正常用户 | 读者想复制文字、开发者想看排版、手机用户想保存图片——全被恶心到 |
| 损害 SEO | 搜索引擎爬虫遇到 JS 阻断可能降低排名 |
| 显得不专业 | 2026 年锁右键/F12 是外行做法 |
| 无法隐藏前端代码 | 浏览器的本质就是下载 HTML/JS/CSS 在本地渲染，无法对用户隐藏 |

已有的实际保护：

- Vue 组件编译后混淆压缩（vite build 产出带 hash 的 chunk）
- 真正敏感的逻辑（密码哈希、用户验证、数据库操作）全在后端
- API 有 JWT 认证 + 权限分层，看得到接口地址也调不了

**结论**：不要锁。担心主题被抄可以在页脚加 CC 协议声明，比锁右键有效 100 倍。

---

## 二、源码审计发现（按优先级）

### P0：本地 .env 曾包含真实 DeepSeek API Key ✅ 已处置

`D:\blog\.env` 曾直接写入真实 API Key。处置记录：

- 2026-09-20 发现该 Key 被引用进安全审计文档，GitHub Push Protection 拦截推送
- 文档重写脱敏（本文件），仓库历史中无原文
- **待办**：如曾怀疑泄露，去 DeepSeek 后台轮换 Key；服务器 `/opt/blog/.env` 确认只存放环境变量版本

**教训**：审计/文档引用凭证时必须脱敏，即使文档"只是本地的"。

### P1：CSP 缺少 connect-src 的 HTTPS 来源

**文件**：`frontend/nginx.conf`

当前 `connect-src 'self'`。当前不影响功能；未来前端需要请求外部 API 时按需扩展。

### P2：client_max_body_size 过大 ⏳ 未修

**文件**：`frontend/nginx.conf`

```nginx
client_max_body_size 1024m;
```

后端 `MAX_UPLOAD_SIZE_MB=10`，但 Nginx 允许 1024MB 上传，攻击者可发大文件消耗带宽。

**建议**：改为 `client_max_body_size 15m;`（略大于后端限制，留 multipart 余量）。

### P2：Caddy HSTS 头缺少 preload ⏳ 可选

服务器 Caddyfile 当前为 `max-age=31536000; includeSubDomains`。如未来提交 HSTS preload list，追加 `; preload`。

---

## 三、已有安全机制清单

| 机制 | 位置 | 作用 |
|------|------|------|
| JWT 认证 + 过期 | `security.py` | access token 30分钟过期，refresh token 30天 |
| bcrypt 密码哈希 | `security.py` | 每次哈希约 300ms，抗彩虹表 |
| 密码强度校验 | `security.py` | 8位+大写+小写+数字 |
| 登录限速 | `auth.py` | 5次/分钟 |
| 账号锁定 | `auth.py` | 5次失败锁30分钟 |
| SuperAdmin 权限 | `deps.py` | 后台操作需 super_admin 角色 |
| must_change_password | `deps.py` | 初始密码强制修改 |
| token_version 机制 | `User` 模型 | 密码重置后旧 token 全部失效 |
| CORS 白名单 | `config.py` | 只允许指定域名跨域 |
| 文件上传校验 | `upload.py` | MIME 类型 + magic bytes 双重验证 |
| 图片压缩 | `upload.py` | 上传图片自动压缩+EXIF 去除 |
| SVG XSS 防护 | `upload.py` | SVG 文件检测 script/iframe/on* 事件 |
| 非 root 运行 | `Dockerfile` | 容器内普通用户运行 |
| server_tokens off | `nginx.conf` | 隐藏 Nginx 版本号 |
| X-Frame-Options DENY | `nginx.conf` | 防止点击劫持 |
| CSP 策略 | `nginx.conf` | 限制脚本/样式/图片来源，编辑器扩展走同源 `/unpkg/` 代理 |
| HSTS | Caddyfile | 强制 HTTPS |
| refresh_token 哈希 | `auth.py` | refresh_token 存 SHA256 哈希而非明文 |
| 隐藏文件拦截 | `nginx.conf` | `location ~ /\.` deny all |

---

## 四、行动清单

### 已完成 ✅

- [x] Nginx 隐藏文件拦截
- [x] robots.txt 补 `Disallow: /admin` + 绝对 URL Sitemap
- [x] 审计文档自身脱敏重写（本文档）

### 待办 ⏳

- [ ] **确认 DeepSeek API Key 状态**：若曾怀疑泄露，去后台轮换
- [ ] **client_max_body_size 改为 15m**
- [ ] Caddy HSTS 加 preload（可选）
- [ ] 有暴力攻击迹象时再加 hCaptcha（可选）

### 明确不做 ❌

- ~~后台路径改名~~：安全混淆，无效且有维护成本
- ~~锁右键/F12~~：损害用户体验，无实际效果
- ~~登录验证码~~：已有三层防护，投入产出比低
- ~~`.htaccess`~~：Nginx 架构不适用

---

## 五、总结

测评意见中属于"看起来安全但实际无效"的措施（后台改名、锁右键/F12）不值得投入。

Docker 三层架构天然隔离了敏感目录（.env 不在容器内、logs 走 stdout、uploads 受控访问），已有三层暴力破解防护（限速+锁定+bcrypt）。剩余待办：**上传体积收紧**和**确认 API Key 状态**，各 5 分钟。
