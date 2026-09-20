import json
import urllib.request
import ssl

API = "https://www.chiyeblog.cn/api/v1"
TOKEN = "pat_22b74d22cc199cfa2d76684ab06c522b10ce713d"
POST_ID = 7

title = "用 Anytype 搭建你的私人知识库：从部署到日常使用"
summary = "零依赖、全离线、端到端加密——Anytype 可能是目前最适合独立开发者的个人知识管理方案。本文覆盖与 Obsidian 的横向对比、自建同步服务器、核心概念详解和日常使用工作流。"

content = """## 为什么不是 Obsidian？

在选个人知识管理工具时，我认真对比了 Anytype 和 Obsidian——目前最强的两个本地优先方案。最终选择了 Anytype，原因如下。

### 横向对比

| 维度 | Anytype | Obsidian |
|------|---------|----------|
| **数据存储** | 本地 + 端到端加密同步 | 本地 Markdown 文件 |
| **同步方案** | 官方免费同步网络 / 自建同步节点 | 官方 Sync 付费（$4-8/月）/ Git / iCloud 等第三方 |
| **加密** | 设备端加密，服务器无法解密 | 官方 Sync 有 E2EE；第三方同步方案不保证 |
| **数据格式** | 结构化对象（Object）+ 数据库视图 | 纯 Markdown 文件 |
| **插件生态** | 较少，核心功能内置 | 1000+ 社区插件 |
| **协作** | 原生共享空间，多人实时协作 | 无实时协作（Sync 共享仓库有限制） |
| **价格** | 完全免费，开源 | 个人免费；Sync $4-8/月，Publish $8/月 |
| **开源协议** | 客户端 + Any Sync 协议均开源 | 客户端闭源免费 |

### 我的选择理由

**1. 同步零成本且可自建**

Obsidian 的核心功能免费，但如果你想要稳定的多端同步，官方 Sync 起步 $4/月（Standard 计划：1 个仓库、1GB 存储、5MB 单文件上限）。当然可以用 Git/iCloud/Syncthing 等第三方方案，但都有各自的问题——Git 对非技术用户不友好，iCloud 只限苹果生态，Syncthing 需要常驻后台。

Anytype 的官方同步网络**完全免费**，而且 Any Sync 协议开源，可以用 Docker 一条命令自建同步节点。对于独立开发者来说，这个差距是决定性的。

**2. 端到端加密是默认行为**

Anytype 的加密是架构层面的——数据在离开你的设备之前就已经加密了，同步服务器只能看到密文。12 个单词的 Key 只存在于你的设备上。

Obsidian 的官方 Sync 也支持 E2EE，但这只是同步插件的一个选项，需要手动开启。如果你用 Git/iCloud 等第三方方案，数据是明文传输和存储的。

**3. 结构化数据更适合知识管理**

Obsidian 的核心理念是"纯 Markdown 文件 + 双向链接"。这个理念很好，但它意味着你很难做结构化查询——比如"显示所有状态为'进行中'的项目"。

Anytype 的 Object 模型天然支持结构化属性、数据库视图、查询筛选。你可以把同一个类型的对象用看板、日历、列表等不同视图展示，这是 Obsidian 需要 Dataview 等插件才能勉强实现的。

### Obsidian 更强的地方

公平地说，Obsidian 在这些方面确实更强：

- **插件生态**：1000+ 社区插件，从 AI 助手到 Dataview 查询，几乎什么都能做
- **数据可移植性**：纯 Markdown 文件，任何编辑器都能打开，20 年后依然可读
- **学习资源**：社区更成熟，教程和模板更多
- **单文件导出**：文件系统即数据库，迁移成本极低

如果你重视极致的插件定制能力和纯文本的可移植性，Obsidian 仍然是更好的选择。但如果你更看重**免费同步、默认加密、结构化数据**，Anytype 是更好的方案。

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

Anytype 不是最快的笔记工具，也不是功能最全的——但它在**免费同步、默认加密、结构化数据**这三个维度上做到了最佳平衡。

Obsidian 有更成熟的插件生态和纯 Markdown 的极致可移植性。但如果你和我一样重视免费同步、不想折腾第三方同步方案、需要结构化的知识管理，Anytype 值得一试。

> 本文基于 Anytype 2026 年 8 月版本，any-sync-bundle v1.1.3。Obsidian 定价数据来自 obsidian.md/pricing（2026 年 3 月验证）。
"""

payload = {
    "title": title,
    "summary": summary,
    "content_markdown": content,
    "reading_time": "10 min",
    "status": "draft",
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{API}/admin/posts/{POST_ID}",
    data=data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
    method="PUT",
)

ctx = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Status: {resp.status}")
        print(f"文章已更新: ID={result.get('id')}, title={result.get('title')}")
        print(f"状态: draft")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')[:500]}")
