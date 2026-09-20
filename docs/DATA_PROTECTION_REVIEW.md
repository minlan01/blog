# 数据资产保护方案复核

复核对象：`D:/blog/docs/DATA_PROTECTION_PLAN.md`

结论：**Conditional NO-GO**

这份方案方向正确，但不能按当前版本直接执行。主要阻塞点在异地备份、`refresh_token` 迁移、以及密钥备份策略。

## P0

### 1. 异地备份不能是可选项

当前主备份落在同一台服务器的 `/opt/blog/backups`，异地备份只写成推荐项。只要攻击者拿到 root，就能同时删业务数据和本地备份。

建议把异地备份提升为强制项，并使用独立凭证、版本保留和不可变/延迟删除策略。

### 2. `migrate_refresh_tokens` 不能单独解决明文 token

当前 `auth.py` 和 `oauth.py` 仍在双写明文 `refresh_token` 和 `refresh_token_hash`，`migrate_refresh_tokens` 跑完后，只要用户重新登录，明文又会重新出现。

建议顺序应是：

1. 先发布 hash-only 代码
2. 再跑迁移清空旧值
3. 最后用 Alembic 删除 `refresh_token` 列

### 3. 备份 `.env` 会扩大密钥泄露面

方案直接把 `.env` 复制进备份目录。如果再同步到云存储，就等于把 SMTP、OAuth、LLM key 和 `SECRET_KEY` 一起同步出去。

远端备份必须加密，恢复流程也要明确是否轮换全部密钥。

## P1

### 4. `SECRET_KEY` 放在 volume 里，不等于防 root 入侵

`/app/data/.secret_key` 只是避免误提交 Git。对 root 来说，它和 `.env` 一样可读。

这项只能算“降低误提交风险”，不能算“入侵后仍保密”。

### 5. 周备份逻辑不完整

`KEEP_WEEKS` 定义了但没有实际使用。周备份 cron 只复制 DB，不包含 uploads、env、文章导出，而且执行时间和日备份也不一致。

建议改成统一脚本，分别生成 daily/weekly/monthly，并覆盖：

- DB
- uploads
- env 或加密后的密钥包
- 文章导出包

### 6. 上传文件备份路径太依赖 Docker 内部实现

脚本直接 tar ` /var/lib/docker/volumes/...` 下的内部路径，迁移服务器或 Docker root 改动后容易失效。

建议用临时容器挂载 `blog-uploads` volume 后打包。

### 7. 缺少备份校验和恢复演练

当前脚本只生成文件，没有做：

- SQLite 完整性检查
- 压缩包可读性检查
- 远端上传成功检查
- 定期恢复演练

建议补这些验证项，否则“有备份”不等于“能恢复”。

## P2

### 8. `SQL 注入几乎不可能` 表述过满

当前 ORM 主路径风险较低，但项目已有迁移、CLI、FTS 等 raw SQL 场景。更稳妥的说法是：主业务查询风险较低，新增 raw SQL 必须审查。

### 9. `client_max_body_size` 应该收紧

当前 Nginx 是 `1024m`，而后端默认上传限制是 `10MB`。前置代理放太大没有收益，只会增加请求压力。

建议收紧到略高于业务上限，例如 `15m`。

## 通过项

- 数据资产识别基本准确
- WAL 和 `busy_timeout` 的方向正确
- 后端使用非 root 用户运行
- 不做数据库透明加密、不做文章 AES 加密、不锁 F12 的判断合理

## 最终判定

这份方案可以作为草案，但**不能直接进入执行**。

先补这几项：

1. 异地备份强制化
2. 备份加密
3. `refresh_token` 改为 hash-only 流程
4. 恢复演练和备份校验

修完后，再进入执行阶段更稳。
