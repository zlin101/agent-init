# Private History 实施计划

Owner 已要求实施；契约由 TASK-0030 持有。默认 Local 不变，不迁移真实资料。

## 冻结设计

1. 复用现有 `~/.trellium/history` Store、immutable SHA-256 版本与 put/get/list/retain_terminal；只保全 terminal TASK 和必要 review ledger，不备份当前 Vault。Private managed material 的“不进 Git”指目标项目的 Git 边界，不禁止本机外部 Store 保存其副本。
2. `vault/project-id` 仍是唯一 canonical UUID 文件。Local tracked；Private 随整个 Vault ignored/untracked。登记仍用现有 stamp files/data role，不复制 UUID、不新增 schema。身份 helper 接受显式 local/private policy，Tracked 拒绝。
3. Private 身份调用前必须已有有效安装 stamp 和精确 private 边界，Git HEAD 是否可判定必须有确定证据；privacy 违规/未知拒绝写入。创建需显式授权，丢失但 inventory/HEAD 已绑定时要求恢复；有效 UUID 复用，Private 登记 baseline 不符拒绝替换，登记失败重试不替换。Local 路径保留原合同。HEAD 路径有无使用 ls-tree --full-tree 的结构结果，保留 monorepo 根坐标及查询失败拒绝。
4. Private 的 UUID 不随 Git clone 自动到新 clone：owner 必须保留/迁移原 UUID，按已知 UUID、artifact id、digest 对 Store get 核对项目证据；在新 private 接入中恢复原 UUID 文件再调用 helper 复用登记。完全丢失所有绑定资料时，不从目录名/remote 猜测项目、不自动声称新绑定延续旧历史。Store 中的 UUID namespace 是历史归属，不能成为第二当前身份 owner。
5. Task/ledger 成组写入和逐份 get 校验，部分失败保留来源、accepted 不回滚、可幂等重试；默认无 cleanup、无旧资料回填。外部历史默认不读、不授予 Authority，不自动恢复任务；跨机器迁移 Store 和 UUID 是手工迁移，不自动同步。

## 最小性与停止条件

首先扩展现有 helper 的 mode gate 与 Private 写前校验，复用 Store，不增加 identity index/manifest、path→UUID registry、CLI、第三种存储格式。通过既有 module API 证明可保全与按已知 UUID 找回即结束；当前知识恢复、默认切换和自动项目发现不混入。

## 实施与验收

- M1：Private 身份 happy path、绑定丢失、缺授权/错误边界、登记失败重试及升级保护的聚焦测试与 helper 扩展。
- M2：canonical Private/Local identity 与 retention 契约、双语实际命令、明确恢复步骤和新 Decision；旧计划/验收作为历史不回写成当时已支持。
- M3：sync 派生副本；双语分发 E2E 保全整组、部分失败重试、删除临时 clone 后找回、重建 Private 恢复已知 UUID；privacy/Local/Tracked 回归与完整测试，实际输出落盘。

环境范围沿用 Store 的可信本机 POSIX filesystem/cooperative writers；不扩大 Windows/NFS/云/磁盘故障保证。全量预存 fixture 失败如实披露；测试均在隔离目录与 Store，不能访问真实用户历史。
