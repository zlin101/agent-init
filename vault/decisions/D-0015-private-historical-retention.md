# D-0015 - Private Historical Retention

Status: Active

Date: 2026-10-01

## Background

Private 起初只解决目标项目 managed material 不进入 Git，跨 clone 恢复是非目标。TASK-0029 随后只为默认 Local 加入 History 保全，并保持 Private 不变。Owner 在三模式梳理后确认：Git 可见性和本机持久保全应分开，并明确要求为 Private 增加 History 储存。

## Decision

- 将 D-0014 的 terminal TASK/必要 review ledger 保全流程扩展到 Private，复用本机 ~/.trellium/history 的 Store 格式、接口、成组 put/get、失败重试与非 Authority 边界；Tracked 不触发，首次接入默认仍 Local。
- vault/project-id 仍是唯一当前身份 owner。Local tracked；Private 随 Vault ignored/untracked，登记现有 stamp files/data role，不复制 UUID 值或引入 schema/index/manifest。
- Private 身份写入前验证有效 stamp、明确的 Git HEAD 证据及精确 private 边界。登记后的 UUID 必须匹配 baseline；绑定缺失/改变要求恢复，不生成替代值。创建仅在 owner 明确首次绑定授权下执行；登记失败保留已创建 UUID，重试复用。
- 新 Private clone 不从 Git 获取身份：owner 保留/迁移原 UUID，按已知 UUID/artifact/digest get 核对历史，完成 private 接入后显式恢复原 UUID 文件并调用 helper 复用登记。完全丢失绑定资料时不按路径/remote/最新版本自动推断，不把新 UUID 当旧历史。UUID namespace 与历史 metadata 只标识历史归属，不成为第二当前身份 owner。
- 外部 Store 是明确的本机历史副本，不进入目标项目 Git；不备份当前 Vault、不同步其他机器、不恢复旧 TASK/Authority，默认不 cleanup/回填。Private privacy Gate 和存量不自动迁移保持不变。

## Rationale

不进入项目 Git 不推出历史可丢弃；可信本机 Store 不违反这一 Git 边界。Local 的 tracked 身份不可原样用于 Private，因此用 ignored 身份与已有 inventory/baseline 保护当前绑定，明确采用手工保留/恢复 UUID 的最小流程，不承诺尚未定义的自动项目发现。

## Alternatives

- 继续 Private clone-only：不能满足 owner 明确的本机历史保全要求。
- Private 身份强制进 Git：违反 Private managed material 边界。
- 新 path/remote→UUID registry、manifest、身份服务或云同步：本次按已知 UUID 找回不需要，增加新的数据格式与故障域，留在 scope 外。
- 将整个 Vault 写入历史后自动恢复：扩大为当前知识/Authority 恢复问题，不混入 TASK/review 保全。

## Impact

实施由 TASK-0030 与验证证据承载。D-0014 的 Local 规则保持；本 Decision 扩展其原“Private 不触发”范围，Private 原计划的 clone-only 是历史基线。Store API/格式、policy/stamp schema、CLI、默认选择、Git 授权及实际环境保证不变。
