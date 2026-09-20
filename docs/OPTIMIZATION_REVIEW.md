# Blog 优化方案复核结论

复核对象：`D:/blog/docs/OPTIMIZATION_PLAN.md` v2.2

复核重点：P0.2.1、P1.5、P4.6.2

## P0.2.1：Alembic baseline

结论：**NO-GO，需要重做迁移链。**

`inspector.has_table()` 只能判断表是否存在，不能发现以下差异：

- 字段、字段类型、可空性和默认值
- 索引、唯一约束、外键和检查约束
- 触发器、视图以及 SQLite FTS 虚拟表

单独增加 `has_column()` 仍然不够，只会形成半幂等的手写迁移。

更严重的问题是，`p0_true_baseline.py` 仍接在 `b4c2d9e8f1a0` 后面。空库执行 `alembic upgrade head` 时，会先运行旧迁移；旧迁移会在不存在的 `posts`、`images` 表上执行 `add_column`，可能在 baseline 执行前就失败。

当前 `D:/blog/backend/app/db/init_db.py` 仍调用 `Base.metadata.create_all()`，这也与 Alembic 作为唯一 schema 入口的目标冲突。

建议：

1. 建立真正的 root baseline，或设计独立的旧库升级路径。
2. 只有在完整 schema 对比一致时才允许 `stamp`。
3. `diff_schema` 至少比较 tables、columns、types、nullable、defaults、indexes、unique、FK、check、trigger 和 FTS。
4. 生产环境移除 `create_all()`，仅在测试或开发环境保留。

## P1.5：SQLite 重建 users 表

结论：**Conditional GO，推荐两阶段迁移。**

`batch_alter_table(recreate="always")` 在 SQLite 下会复制整张 `users` 表、删除旧表，再重命名新表。因此它不是普通的字段改名操作。

主要风险：

- users 数据量较大时会产生明显耗时、写锁和额外磁盘占用。
- `comments.user_id` 外键指向 `users.id`。`PRAGMA foreign_keys=ON` 时，删除旧表可能失败；关闭时又必须执行完整性检查。
- Alembic 通常会重建表内索引和约束，但外部触发器、视图和特殊索引需要单独确认。
- 当前 downgrade 会清空 token，回滚不会恢复原 token，属于有意的数据失效，必须明确记录。

推荐流程：

1. 先新增 nullable 的 `refresh_token_hash`。
2. 发布代码改为只读写 hash，并清空旧明文 token。
3. 后续维护窗口再删除 `refresh_token`。

如果坚持一次重建，必须增加真实数据库备份、恢复演练、`PRAGMA foreign_key_check`、行数和关键数据校验、索引/FK/触发器校验，以及迁移耗时测试。

## P4.6.2：Nginx posts 正则

结论：**当前 slug 规则下可行，但需要补充边界验收。**

对于 `location ~ ^/posts/[^/]+$`：

| 请求路径 | 行为 |
|---|---|
| `/posts` | 不匹配，走 SPA 列表页 |
| `/posts/` | 不匹配，走 SPA fallback |
| `/posts/example-slug` | 匹配，走后端文章壳页面 |
| `/posts/example-slug?x=1` | 仍然匹配，query string 不参与 location 匹配 |
| `/posts/example/child` | 不匹配，回到 SPA fallback |
| `/posts/example-slug/` | 不匹配，回到 SPA fallback |

当前 `D:/blog/backend/app/schemas/post.py` 已禁止 slug 包含 `/`，所以单段 slug 与该正则一致。但历史数据或绕过 API 写入的 slash slug 会漏掉 OG 壳页面，并可能被 SPA fallback 静默接管。

必须验收：

- `/posts` 返回前端列表页。
- `/posts/example-slug` 返回包含 OG meta 的后端 HTML。
- `/posts/example/child` 返回明确的 404 或重定向，不能静默返回 SPA。
- 明确 `/posts/example-slug/` 是重定向还是合法页面。

如果未来支持层级 slug，不能只改 Nginx，还要同步修改 FastAPI 路由、slug 校验、canonical、缓存键和 SEO 逻辑。

## 最终判定

| 项目 | 判定 |
|---|---|
| P0.2.1 baseline | NO-GO，必须重做迁移链和完整 schema 对比 |
| P1.5 users 重建 | Conditional GO，推荐两阶段迁移 |
| P4.6.2 Nginx 正则 | 当前 slug 合约下可行，必须补边界测试 |

本次仅新增审核文档，未修改项目代码。
