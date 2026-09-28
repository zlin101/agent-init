# D-0010 - Git 接入持久性 Gate（2026-09-18）

Status: Active

## Background

TASK-0013 确认 2026.09.7 存在接入假健康：`adopt` 生成完整协作层后核心未进 Git `HEAD`，fresh clone 全部丢失，`check` 仍报 0/0。owner 批准 Level C 立项并把"核心未进 HEAD"定为 error。P0/P1 预注册消融的正式裁决为 Inconclusive：P1 H3=1，未满足冻结 Gate 的 H1=H2=H3=0，因此不授权双语 Skill 候选契约；checker 与场景无关的 CLI 提醒独立修复。

## Decision

1. `adopt` 只输出场景无关的 `generated ≠ durable` 提醒与后续检查顺序，不声称本次生成文件的实际提交状态；双语 Skill 保持 P0，不加入未通过 Gate 的候选契约。
2. checker 以安装版本戳派生协作核心集合，机械核对 `HEAD`：当前 stamp 损坏报 `CORE_STORAGE_INVALID` error；未提交或 HEAD stamp 与当前协议版本/核心集合不相容报 `CORE_STORAGE_UNCOMMITTED` error；被 ignore 规则误伤报 `CORE_STORAGE_IGNORED` error；Git 验证命令失败报 `CORE_STORAGE_UNVERIFIED` error，非 Git 报同码 warning。local 模式以无写入 sentinel 验证边界（`LOCAL_BOUNDARY_UNCONFIGURED` warning / `LOCAL_BOUNDARY_OVERREACH` error / `LOCAL_BOUNDARY_UNVERIFIED` error）。checker 只读：不自动 `git add`/commit/push、不改 `.gitignore`、不运行 clone；fresh clone 是验收动作，不进入日常 check。
3. 版本控制动作永远归属用户：工具与 Agent 不得自动 commit/push。

## Rationale

场景 A 中 P1 的遗漏减少只是记录性收益；场景 B 中 P1 仍把 durable namespace 误归 local，违反冻结硬指标，不能据此增加长期 Skill 文本。机械 Gate 不依赖模型遵循，HEAD 事实与 fresh clone 可见性等价且成本低（M0 fixture 矩阵与 fresh-clone 对照冻结）。

## Impact

已 adopted 且核心未提交或当前 stamp 与 HEAD stamp 不相容的项目升级到 2026.09.8 后 `check` 从 0/0 转为 error——真实缺陷暴露而非回归，修复动作是用户提交完整一致的核心状态（本仓库 owner 未提交的 `docs/engineering/` 与 stamp 核心集合变化即真实样本）。Orion 升级与 fresh-clone 验收留给 TASK-0004。消融材料、投放偏差登记与逐格评分见 `docs/evals/adoption-durability-2026-09/`。
