import json
import urllib.request
import ssl

API = "https://www.chiyeblog.cn/api/v1"
TOKEN = "pat_22b74d22cc199cfa2d76684ab06c522b10ce713d"

title = "用 Anytype 搭建你的私人知识库：从部署到日常使用"
slug = "anytype-personal-knowledge-base"
summary = "零依赖、全离线、端到端加密——Anytype 可能是目前最适合独立开发者的个人知识管理方案。本文覆盖自建同步服务器、核心概念详解和日常使用工作流。"

content = """## 为什么选择 Anytype

用过 Notion、Obsidian、Logseq 之后，我的核心痛点是：

- **Notion**：数据在云端，断网就废，且隐私不可控
- **Obsidian**：本地文件不错，但同步要么花钱要么折腾 Git
- **Logseq**：大纲式很棒，但移动端体验拉胯

Anytype 的解法很直接：**本地优先 + P2P 同步 + 端到端加密**。你的数据先存在设备上，然后通过 Anytype 的中继网络（或你自己的服务器）在设备间同步。没有任何中间人能看到你的内容。

### 核心特点

| 特性 | 说明 |
|------|------|
| **离线优先** | 所有数据本地存储，断网完全可用 |
| **端到端加密** | 数据在设备上加密后才同步，服务器看不到明文 |
| **P2P 同步** | 同一局域网下直接设备间同步，不经过服务器 |
| **开源自协议** | Any Sync 协议开源，可自建同步节点 |
| **跨平台** | macOS / Windows / Linux / iOS / Android 全平台原生应用 |

---

## 第一部分：自建同步服务器

Anytype 默认提供免费的官方同步网络，但如果你想要完全控制数据，可以自建。

### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **官方网络** | 零配置，免费 | 数据经过官方服务器（虽然加密） |
| **any-sync-bundle** | 一条命令搞定，资源占用低 | 单节点，无水平扩展 |
| **any-sync-dockercompose** | 官方完整架构 | 组件多，资源占用高 |

> **推荐**：个人使用选 `any-sync-bundle`，60 秒部署完成。

### 用 any-sync-bundle 一键部署

#### 前置条件

- 一台 Linux 服务器（Ubuntu 22.04+，最低 1GB 内存）
- Docker 已安装
- 开放端口：TCP `33010`、UDP `33020`

#### 部署步骤

```bash
# 拉取镜像并启动（替换 IP 为你的服务器 IP）
docker run -d \\
  --name anytype-sync \\
  --restart unless-stopped \\
  -e ANY_SYNC_BUNDLE_INIT_EXTERNAL_ADDRS="203.0.113.11" \\
  -p 33010:33010 \\
  -p 33020:33020/udp \\
  -v $(pwd)/data:/data \\
  ghcr.io/grishy/any-sync-bundle:1.1.3-2025-12-01
```

启动后，`./data/client-config.yml` 就是客户端配置文件。

#### 配置防火墙

```bash
sudo ufw allow 33010/tcp
sudo ufw allow 33020/udp
```

#### 如果你有域名 + HTTPS

推荐用 Caddy 做反向代理（自动 HTTPS）：

```caddyfile
sync.yourdomain.com {
    reverse_proxy localhost:33010
}
```

### 连接客户端

1. 打开 Anytype 桌面端
2. 退出当前账号
3. 在欢迎界面点击右上角 **齿轮图标**
4. **Network** 选择 **Self-hosted**
5. 上传 `client-config.yml` 文件
6. 点击 **Save**
7. 创建新身份或登录已有身份

> **重要**：建议为自建网络创建专用身份，不要和官方网络混用。

---

## 第二部分：核心概念

### Vault（保险库）— 你的账户

创建账户时会生成 12 个单词的密钥（Key），**这是唯一能解密你数据的钥匙**，务必离线保存。

### Space（空间）— 工作空间

Space 是 Vault 内的独立工作区。可以为不同领域创建不同 Space：
- 个人笔记 / 工作项目 / 阅读笔记 / 目标管理

### Object（对象）— 万物皆对象

**页面、任务、项目、人、图片、书——一切都是 Object**。

和文件夹的区别：
- 文件夹问"这个放在哪？" → 只能放一个地方
- 对象问"这与什么相关？" → 可以同时关联多个东西

创建对象：`Cmd/Ctrl + N`，或编辑器内输入 `/` 召出命令菜单。

### Type（类型）— 对象的蓝图

| 内置类型 | 用途 |
|---------|------|
| Page | 通用文档 |
| Task | 任务 |
| Project | 项目 |
| Book | 书籍 |
| Person | 人物 |
| Note | 速记 |

也可以创建自定义类型——比如"播客"、"代码片段"、"食谱"。

### Property（属性）— 描述和连接

属性是附加在对象上的标签，既描述对象、又连接对象。

- **描述型**：状态 = 进行中、优先级 = 高
- **连接型**：负责人 → 张三（一个 Person 对象）

### View（视图）— 组织和可视化

- **List** — 简单列表
- **Grid** — 类电子表格
- **Kanban** — 看板
- **Calendar** — 日历
- **Gallery** — 画廊
- **Graph** — 知识图谱

### Collection vs Query

| 概念 | 特点 | 类比 |
|------|------|------|
| **Collection** | 手动添加对象 | 播放列表 |
| **Query** | 按条件自动筛选 | 智能歌单 |

---

## 第三部分：搭建你的知识库

### 步骤 1：规划类型系统

不要一上来就创建一堆自定义类型。先用内置的，不够再扩展。

推荐起点：Book（读书笔记）、Project（技术项目）、Task（待办）、Note（随手记）。

### 步骤 2：建立属性体系

```
Book 类型：
  - 作者 → Person
  - 评分 → Number (1-5)
  - 状态 → Select (想读/在读/已读)

Project 类型：
  - 状态 → Select (规划中/进行中/已完成)
  - 技术栈 → Multi-select
  - 仓库链接 → URL
```

### 步骤 3：创建模板

模板让你每次新建对象时自动填充结构。比如"读书笔记模板"可以预设：书籍信息区、核心观点区、摘录区、读后感区。

### 步骤 4：建立视图

- Book → 按"状态"分组的看板视图
- Task → 按"截止日期"排列的日历视图
- Project → 按"状态"筛选的列表视图

---

## 第四部分：日常使用工作流

### 速记捕获

随手记用 **Note** 类型，不纠结分类。后续整理时再用属性和链接归位。

### 双向链接

在编辑器里输入 `@` + 对象名就能插入链接。反向链接自动生成，不用手动维护。

比如在读书笔记里写"这本书提到了 @React"，你的 React 对象就会自动显示这条反向引用。

### 知识图谱

Graph 视图能可视化所有对象的关联。随着知识积累，你会看到一张越来越密集的网——这就是你的个人知识图谱。

### 移动端配合

Anytype 的移动端是原生应用，通勤路上记笔记、整理任务、查看项目，全部离线可用。

---

## 维护建议

### 备份

- **导出 Key**：12 个单词的密钥写在纸上
- **本地备份**：定期导出 Space 数据
- **自建服务器备份**：定时备份 `data/` 目录

### 性能

- 单个 Space 建议不超过 5000 个对象
- 自建服务器内存占用约 250-300MB，1G 内存够用

### 安全

- 不要把 Key 分享给任何人
- 自建服务器建议配置 HTTPS
- 定期更新 any-sync-bundle 版本

---

## 总结

Anytype 不是最快的笔记工具，也不是功能最全的——但它在**隐私、离线、可自建**这三个维度上做到了最佳平衡。

如果你和我一样重视数据主权，又受够了 Notion 的断网即废和 Obsidian 的同步折腾，Anytype 值得一试。

> 本文基于 Anytype 2026 年 8 月版本，any-sync-bundle v1.1.3。
"""

payload = {
    "title": title,
    "slug": slug,
    "summary": summary,
    "content_markdown": content,
    "reading_time": "8 min",
    "status": "draft",
    "is_featured": False,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{API}/admin/posts",
    data=data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
    method="POST",
)

ctx = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Status: {resp.status}")
        print(f"文章已创建: ID={result.get('id')}, slug={result.get('slug')}")
        print(f"状态: draft (草稿)")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')[:500]}")
