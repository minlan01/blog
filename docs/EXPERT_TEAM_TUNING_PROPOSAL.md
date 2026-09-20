# 专家团配置调优方案

> 基于本博客项目 P0/P1/P2 实际使用后的复盘结论

---

## 一、当前问题诊断

### 1.1 配置过重

当前专家团：**13 个角色 + 3 个 Gate + 主理人中转**

| 角色 | 类型 | 对个人博客的实际价值 |
|------|------|---------------------|
| product-domain-lead 明察秋 | 分析型 | ❌ 低（需求你自己想清楚了） |
| architecture-governor 构思远 | 分析型 | ✅ 高（抓架构盲点） |
| security-governor 严守一 | 分析型 | ✅ 高（安全审查） |
| execution-consistency-engineer 一致恒 | 设计型 | ❌ 低（分布式一致性，博客用不上） |
| backend-engineer 端稳成 | 设计型 | ⚠️ 中（你已代行） |
| frontend-engineer 界悦然 | 设计型 | ⚠️ 中（你已代行） |
| data-migration-engineer 迁无失 | 设计�� | ⚠️ 中（Alembic 你已代行） |
| platform-sre-engineer 台固安 | 设计型 | ❌ 低（2 核 2G，部署简单） |
| test-automation-engineer 测无遗 | 分析型 | ⚠️ 中（测试策略有价值） |
| security-validation-engineer 攻未然 | 分析型 | ⚠️ 低（个人博客对抗测试过重） |
| observability-incident-engineer 观微知 | 设计型 | ❌ 低（博客不需要 SLO/Runbook） |
| docs-release-engineer 文同步 | 设计型 | ❌ 低（你直接出文档） |
| independent-release-reviewer 独立明 | 分析型 | ✅ 高（发布前独立复核） |

**结论：真正有价值的只有 3 个**——架构师、安全官、独立审查员。其余 10 个对个人博客都是过度设计。

### 1.2 TeamCreate 可靠性问题（实测）

| 现象 | 根因 | 影响 |
|------|------|------|
| 严守一 SendMessage 持续失败 | 会话长时间间隔后"Not in a team" | 结果丢失，需重调度 |
| 团队上下文丢失 | 会话连续性要求高 | SendMessage 抛错 |
| 成员间无法直接协作 | 必须经主理人中转 | token 翻倍 |

**实测对比**（本博客 P2-2）：

| 调度方式 | 可见性 | 可靠性 | 失败重试成本 | token |
|---------|--------|--------|-------------|-------|
| TeamCreate + SendMessage | ✅ 你看到团队聊天 | ⚠️ 不稳定 | 高（重建团队） | 高 |
| Agent 直接调用 | ❌ 后台 | ✅ 稳定 | 低（再调一次） | 中 |
| 主理人自查（不调度） | ❌ 只看汇总 | ✅ 最稳 | 零 | 零 |

---

## 二、推荐配置：精简方案

### 2.1 角色精简到 3 个

| 保留角色 | 触发场景 | 调度方式 |
|---------|---------|---------|
| **architecture-governor** 构思远 | 架构变更 / 复杂功能实现 / 代码审查 | Agent 后台调用 |
| **security-governor** 严守一 | 认证授权 / 数据流 / 上线前安全审查 | Agent 后台调用 |
| **independent-release-reviewer** 独立明 | 部署上线前最终复核 | Agent 后台调用 |

**砍掉/合并的角色**（10 个）：
- ❌ product-domain-lead → 需求你自己定
- ❌ execution-consistency-engineer → 分布式特性，博客用不上
- ⚠️ backend-engineer / frontend-engineer / data-migration-engineer → 合并到"主理人代行"，只在审查节点拉架构师看
- ❌ platform-sre-engineer → 2 核 2G 部署简单
- ⚠️ test-automation-engineer → 合并到 architecture-governor 的审查范围
- ❌ security-validation-engineer / observability-incident-engineer → 个人博客过重
- ❌ docs-release-engineer → 你直接出文档

### 2.2 Gate 精简到 2 个

| Gate | 触发时机 | 裁决者 | 通过条件 |
|------|---------|--------|---------|
| **Gate A** 方案审查 | 复杂功能设计完成后、实现前 | architecture-governor（+ security-governor 若涉及安全） | 无 P0 阻断 |
| **Gate B** 上线审查 | 部署前 | independent-release-reviewer | PASS |

**取消的 Gate**：
- ❌ 原来的"Gate B 实现审查" → 合并进 Gate A 的二次审查（同一专家，避免重复调度）
- ❌ "每阶段都审查" → 改为"只在高风险节点审查"

### 2.3 调度策略：按风险分级

| 任务复杂度 | 例子 | 是否调度专家 |
|-----------|------|-------------|
| 🟢 常规修改 | 改 CSS / 加字段 / 调样式 / 小 bug | ❌ 主理人自查 |
| 🟡 中等功能 | 新增 API / 前端组件 / 表结构变更 | ⚠️ 实现后拉架构师审一次（Gate A） |
| 🔴 高风险/复杂 | FTS5 / 认证授权 / 数据迁移 / 并发控制 | ✅ 实现前设计方案审查 + 实现后代码审查（双重） |
| 🚀 上线 | 部署到服务器 | ✅ 必走 Gate B |

**调度方式统一为 Agent 后台调用**，不用 TeamCreate。你（用户）在对话里能看到我调度了谁、审查结果如何——虽然看不到团队聊天界面，但结果透明可追溯。

---

## 三、三种模式 token 对比

基于本博客实测数据粗估：

| 模式 | P0 token | P1 token | P2-2 token | 上线 token | 总计 |
|------|---------|---------|-----------|-----------|------|
| **当前配置**（13 角色 + 团队） | 高 | ��� | 极高 | 高 | 🔴 最贵 |
| **推荐配置**（3 角色 + 2 Gate + Agent 调用） | 零（自查） | 零（自查） | 中（架构+安全各审1次） | 中（独立审查1次） | 🟡 适中 |
| **极致省 token**（完全不调度） | 零 | 零 | 零 | 零 | 🟢 最省 |

**推荐配置的 token 节省点**：
- P0/P1 完全自查，零调度（节省约 40%）
- P2 只在 FTS5 这类复杂功能调度（节省约 60%）
- 上线只调一次独立审查（保留最后一道关）

**推荐配置的质量保障**：
- 复杂功能仍有独立 context 审查（防主理人盲点）
- 上线前有独立复核（防遗漏）
- 常规修改靠主理人自查（接受小盲点，换取 token）

---

## 四、实施步骤（如确认）

1. **修改主理人 prompt**（`super-agent-delivery-team-team-lead.md`）
   - 删除 10 个不常用角色的描述
   - Gate 从 3 个改为 2 个
   - 调度策略改为"按风险分级"
   - 明确"默认 Agent 后台调用，不用 TeamCreate"

2. **可选：删除多余专家成员文件**
   - 保留 3 个 .md 文件
   - 其余 10 个归档到 `_archive/`

3. **SOP 更新**
   - 新增"风险分级决策树"
   - 明确每种复杂度的调度策略

---

## 五、决策清单

请你选一个：

- **方案 A：按本推荐配置调整**——3 角色 + 2 Gate + Agent 调用 + 风险分级
- **方案 B：保持当前配置**——13 角色 + 3 Gate + TeamCreate（不省钱，但保持完整流程）
- **方案 C：极致省 token**——完全不调度，主理人自查为主（最省，但有盲点）
- **方案 D：中间路线**——保持 13 角色定义不删，但实际只调度 3 个常用角色，调度方式改为 Agent 后台调用

我个人推荐 **方案 A**，理由：
- 砍掉冗余角色减少认知负担
- 2 个 Gate 够用（博客不需要 3 道关）
- Agent 后台调用比 TeamCreate 可靠
- 风险分级让 token 花在刀刃上

---

_文档 v1.0 · 2026-07-28 10:16_
