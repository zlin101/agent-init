# Decisions

长期决策记录。当前任务进展放 `vault/runtime.md` 或 `vault/tasks/*`。

每条决策标注状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。默认 `Active`。

超过 150 行或 8 条完整记录时索引化：本文件变纯索引（每条 1-2 行），正文迁入 `vault/decisions/D-xxxx-slug.md`。ID 顺序分配。

## 决策索引

- D-0001 · Canonical K1-K4 实验契约 · Active · shadow 观测以 2026-09-04 计划第 2 节为唯一定义，旧标签映射为 A1/A2/canonical K2，历史不改写 · 2026-09-08
- D-0002 · Self-hosting vault check 进入 CI 门禁 · Active · PR 与 main/develop push 运行只读 check；写权限仅限 PR self-heal job，push 任务严格只读 · 2026-09-08
- D-0003 · Release 元数据降为可选改进 · Superseded by D-0013 · 历史版本曾要求 GitHub Release；2026-09-28 起 Trellium 改为只发布 tag · 2026-09-08
- D-0004 · Context 功能 No-Go · Active · M4/`trellium.py context` 未授权不实现；AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件 · 2026-09-08
- D-0005 · 覆盖计数单源 · Active · 覆盖事件以 shadow ledger append-only 行为唯一事实源；数字汇总仅为 dated derived snapshot；runtime/handoff 只引用不维护副本 · 2026-09-08
- D-0006 · Local TASK 私有边界 · Active · local TASK 是私有可丢弃工作日志，只有长期约束蒸馏进 canonical 文件；missing-local warning 不授予恢复权限；tracked 校验保持严格 · 2026-09-09
- D-0007 · 只读 status 摘要命令 · Active · `trellium.py status`（text/JSON v1）编译 check 已校验的状态层：lifecycle/authority 只来自有效状态块，closed 只计数，unresolved 原因按 finding phase 结构化推导且不伪造；不扩 schema、不是 approval inbox · 2026-09-09
- D-0012 · 首次接入默认 local TASK storage · Active · Skill/Agent 先询问并推荐 local，未指定时按 local 执行；只有 TASK/review/archive 留在本地，核心仍 tracked；不新增 CLI API，存量策略不自动迁移 · 2026-09-28 · 正文见 `vault/decisions/D-0012-local-default-task-storage.md`
- D-0013 · Trellium 静默发布仅推送 tag · Active · 后续版本不创建 GitHub Release，也不生成 release 文本；`--fetch` 与显式 `install.sh --version` 已支持 tag，未指定版本的安装只会停留在最后一个 Release · 2026-09-28 · 正文见 `vault/decisions/D-0013-tag-only-releases.md`

## D-0001 - Canonical K1-K4 实验契约（2026-09-08）

Status: Active

### Background

shadow ledger 初版使用的 K1-K4 标签与 2026-09-04 实施计划第 2 节预注册的假设存在同名异义（初版 K2/K3/K4 与 canonical K2/K3/K4 含义不同），继续混用会使试点结论不可比。

### Decision

以 2026-09-04 计划第 2 节为 canonical K1-K4 唯一定义；初版 K2（runtime 投影）与初版 K4（预算阈值）降为辅助指标 A1/A2，初版 K3（tracked/local）改称 canonical K2；历史观测行不删除、不改写。映射记录见 `vault/details/shadow-run-2026-09.md` 顶部 2026-09-08 reconciliation 块。

### Rationale

跨项目证据要求（两个真实项目、至少 10 次状态变化）挂在 canonical 假设上；不消除同名异义，K3/K4 的证据永远无法积累，kill criterion 无法评估。

### Alternatives

- 保留初版标签并改写计划定义：被否，预注册指标不容事后修改。
- 删除初版表格重建：被否，违反 append-only 与"不改写历史观测"。

### Impact

后续 Agent 记录 shadow 观测时必须按 canonical 定义选表；引用"K1-K4"时须落到具体计划段落，不得只写缩写。

## D-0002 - Self-hosting vault check 进入 CI 门禁（2026-09-08）

Status: Active

### Decision

`.github/workflows/skill-sync.yml` 在 PR 与 push（`main`、`develop`）上运行只读 `python3 scripts/trellium.py check . --format json`；checker error（exit 2）使 job 失败，warning 保持既有 exit-0 语义。权限按事件最小化：写权限（`contents: write`、`pull-requests: write`）仅存在于 PR 专用 `sync` job（self-heal 所需）；push 专用 `gate` job 无 job 级权限提升，只继承 workflow 级 `contents: read`。CI 不修改 `vault/`。

### Rationale

本仓库以 tracked 模式自托管 Trellium，vault 结构漂移应在合并前机械可见；同时分支 push 不需要任何写 token，单一 job 携带写权限属于不必要的暴露面。

### Alternatives

- 独立新 workflow：被否，最小修改原则，避免第二套触发面。
- 单一 job 承载 PR 与 push：被否（review round 1 R1），`permissions` 只能按 job 声明，单 job 无法让 push 事件摆脱写权限。
- warning 也使 job 失败：被否，擅自加严会改变 checker 既有退出码语义。

### Impact

向 `develop` 或 `main` 推送前先在本地跑同一命令；CI 报 error 时修 vault 结构，而不是放松门禁；后续改 workflow 时保持"push 路径零写权限"不变。

## D-0003 - GitHub Release 元数据降为可选改进（2026-09-08）

Status: Superseded by D-0013

### Background

2026.09.3 Release 已发布且 `releases/latest` 解析正确，但 API 返回 `name=""`、`body=""`；TASK-0002 原契约把标题与 notes 列为验收 Gate，形成唯一残余缺口。

### Decision

Owner 于「09.3 Post-release Validation」方案 M0 决定：Release 验收 Gate 为——指向既有正确 tag、非 draft、非 prerelease、`releases/latest` 解析到该版本；标题与 notes 降为可选改进，不再阻塞任务关闭。

### Rationale

`install.sh --fetch` 等所有机器路径只依赖 tag 与 latest 解析；标题/notes 仅影响人类阅读体验。为可选的人类体验阻塞治理闭环，摩擦大于收益。

### Alternatives

- 阻塞等待 owner 在 UI 补齐元数据：被否，收益不抵摩擦；事实仍记录在 TASK-0002 的 Optional 条目中，随时可补。

### Impact

后续 Release 类任务的验收不再把元数据当 Gate；引用本决策时注意其适用边界——发布对象本身缺失或 tag 错误仍是不折不扣的失败。

## D-0004 - Context 功能 No-Go 与重开条件（2026-09-08）

Status: Active

### Background

「09.3 Post-release Validation」M1 冷启动基线（S1-S7，7 个独立新会话）结果：判断准确率 7/7、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0，每场景读取 5-16 个文件。M3 三条件中条件 1（≥2 次可复现判断失败）不成立、条件 2（读取成本持续明显）未被证实、条件 3（手工 manifest A/B ≥30% 降本）未测试；M2 无第二项目。Agent 建议 No-Go。

### Decision

Owner 于 2026-09-08 采纳 No-Go：当前不进入 M4，不立项、不实现 `trellium.py context`；暂不补做手工 Manifest A/B；AGENTS.md → vault 必读路径继续作为默认方案。Context 评估重开仅限：

1. 真实工作累计出现至少两次可复现的契约、授权或证据边界误判；
2. 持续记录到明显的读取成本，并补齐 bytes/耗时数据；
3. Owner 明确批准手工 A/B，且结果证明成本降低至少约 30%，同时没有准确率、越权和验收判断退化。

### Rationale

开发新功能的举证责任未满足：M1 未显示任何判断失败；读取成本有界且在协议设计内工作。M1 的评分污染（3/7 场景读到评分 key）与 bytes/耗时数据缺失限制结论强度，但不构成 Go 证据。M2 第二项目试点继续用于验证 K1-K4，但不阻塞本决策。

### Alternatives

- 立即实现 context 命令：被否，无失败或成本证据支撑。
- 立即补做手工 A/B：被否，owner 判定暂无必要；条件 3 保留为重开路径之一。

### Impact

任何 Agent 不得在无新任务契约的情况下实现 context/evidence 类功能；以本决策为"不实现"依据时，须同时检查三条重开条件是否已被真实证据触发。重开证据（误判事件、成本记录）必须先登记在 vault 观测文件中，不得口头声称。

## D-0005 - 试点覆盖计数单一事实源（2026-09-08）

Status: Active

### Background

试点覆盖计数（TASK / lifecycle 转换 / blocked→active / handoff）曾同时独立存在于 runtime 进度行、handoff 条目与 shadow ledger，发生过真实漂移：runtime/ledger 写"3 个真实 TASK"而 checker 报 `current_task_files: 4`，checker 对自然语言计数 0 finding，靠人工复核才发现（ledger canonical K3 行有档）。

### Decision

覆盖事件的唯一事实源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行；任何数字汇总只是带"截至日期/commit"的派生快照（derived snapshot），不得作为长期 owner；`vault/runtime.md` 不维护可独立修改的详细数字副本，只保留一句话状态、指向 ledger 的路径与未满足的主要 Gate；`vault/handoff.md` 不保存累计计数（条目中的数字仅为撰写时点快照）。不为此扩展 checker、不新增 schema、不做自动生成器。

### Rationale

消除多 owner 漂移的最小手段是减少 owner 数量，而不是增强校验工具。checker 的自然语言盲区已登记（canonical K3 遗漏栏），按 D-0004 的精神不以扩工具响应单次事件。

### Alternatives

- 增强 checker 解析自然语言计数：被否，违反最小 checker 边界，且计数 schema 化属于过度设计。
- 维持多处计数现状：被否，漂移已实际发生一次。

### Impact

后续 Agent 更新覆盖信息时：先写 ledger 事件行，再（可选）刷新 dated 快照；runtime 只写一句话+指针。在其他文件发现独立维护的计数副本时，按本决策收敛并引用 D-0005。

## D-0006 - Local TASK 私有边界与 clone-safe 投影（2026-09-09）

Status: Active

### Background

local TASK 设计上就是 ignored 的私有工作日志（不进仓库、可丢弃），但 09.3 的 checker 把 fresh clone 中 runtime 指向的 missing local TASK 判成与 tracked 丢失相同的 error，没有表达"按策略不可见"与"真丢失"的区别；且 local 任务进入 accepted 前没有显式的长期知识处置检查点。

### Decision

local TASK 保持私有、临时、低仓库负担：任务关闭前把会约束未来实现的最小结论蒸馏到 canonical 文件（decisions/project/details/公开契约），没有则记录 `none`；蒸馏是人工 review gate，不做自动提取。runtime 中 missing open local TASK 产生 clone-safe warning，明确"可能是正常 fresh clone 也可能误删"，并声明 runtime 摘要不授予任何 Authority——继续任务必须取回原任务文件或经 owner 批准重建契约。closed local TASK 不得留在 runtime 热路径。tracked 模式的全部严格校验保持不变。

### Rationale

local TASK 的价值在于私有和低负担；把它重新包装成需要发布的资产会制造重复事实源。机器无法判断"什么值得长期保留"，这是人工判断；机器能做的是把证据边界表达清楚并 fail closed。

### Alternatives

- 自动发布/归档 local TASK 或 publish generator：被否，制造第二事实源。
- 把 missing local 静默忽略：被否，无法区分正常 fresh clone 与误删，且会诱导 Agent 从 runtime 摘要恢复越权工作。

### Impact

Agent 遇到 missing local TASK 的 runtime 行时：不据此获得授权、不重建契约，先向 owner 取回原文件或申请重建。`2026.09.4` 起新关闭的 local 任务需人工完成 Durable Knowledge Disposition；历史任务不批量回填。tracked 项目行为零变化。

## D-0007 - 只读 status 摘要命令（2026-09-09）

Status: Active

### Background

owner 在 09.3–09.4 期间反复让 Agent 重读 runtime/TASK 手工汇总进度（A+B 级证据）；2026.09.5 审计将其选为唯一开发候选（TASK-0008），实现前完成 S0/S1 双臂盲测（原始记录存 `vault/details/status-blind-test-2026-09/`），owner 两轮 review 后验收。

### Decision

`trellium.py status <target>`（`--format json` 可选）作为只读 owner 状态摘要：lifecycle/authority 只来自有效的 trellium-task-state 块；closed 只进计数；drift 降级 unresolved、不裁决；unresolved 原因按 finding phase（task-state/runtime-projection）结构化推导，不伪造码；文本与 JSON v1 同源。它是状态摘要，不是 approval inbox。

### Rationale

复用 check 的单一事实源而不新增状态 owner；盲测显示 S1 的正确性优势来自内建 open/closed 分类学与 fail-closed 投影抑制，而非仅 bytes 更小。

### Alternatives

- 持久 inbox/approvals 文件：被否，会形成第二状态 owner。
- 把 owner 视图并入 check：被否，会污染 check 的稳定 schema 与退出码。
- runtime 自动生成器：被否，写放大且制造第二事实源。

### Impact

后续把 status 扩展为 inbox/approval 推断、增加字段或改变 JSON v1 形状，需新决策；unresolved 原因推导按 phase 跟随 checker 演进，无需维护代码清单；引用本命令边界时以本决策与 TASK-0008 契约为准。

## D-0008 - Review Pack 方向结论与 R2 处置（2026-09-13）

Status: Active

### Background

Codex 深度使用反馈指出 reviewer 不应只拿到 diff 而缺少契约/证据边界（TASK-0009 的需求源）。TASK-0009 以 TASK-0007/0008 的真实历史 review 快照完成 R0（reviewer 自行组装）与 R1（手工最小 Review Pack）消融：19 个盲测会话（12 有效 / 7 污染作废 / 5 infra 中断留档），预注册→快照→会话→评分全链路 Git DAG 可证，独立 review 四轮，owner 两轮 review。

### Decision

R1 正式判定为 **Inconclusive**（计划 §10.1 封顶：负对照被两处真实 `status` 缺陷失效，control_invalidated 双登记，均经 scorer 与独立 review 复现）。**R2（确定性 review-pack CLI）本周期不实现、不提案**；重开需 owner 另立 Level C 任务。记录性发现（非正式结论）：S1 known-P0/P1 召回 25%、wall-clock 中位数 +24.4%、上下文组装效率真实改善（visible −57.6%、vault opens −46.2%）。owner 指令：不得恢复早期 No-Go 或 "over-determined" 表述。

### Rationale

负对照被真实缺陷失效后，实验无法输出任何方向的终局结论；"核心数字正确"不能替代全部投影与审计记录同步正确（owner review 两轮共 8 项发现的教训）。

### Alternatives

- 维持 No-Go：被 owner 否决，违反冻结封顶规则。
- 立即实现 R2：被否，消融未证明收益且两处 status 缺陷优先（TASK-0010）。

### Impact

Review Pack 不进入 2026.09.x 路线；重开仅经 owner Level C。三项 `status` 缺陷另立 TASK-0010（P1/P1/P2，owner severity 裁定）。实验原始材料与脱敏方案见 `docs/evals/review-pack-2026-09/`。

## D-0009 - 项目工作 Skill 方向关闭（2026-09-18）

Status: Active

### Background

TASK-0011 按预注册 A0/A1 消融（三场景 × 两臂 × 独立首答）验证项目级工作 Skill：两臂全场景 0 关键遗漏 / 0 需要纠正 / 0 硬指标违规（A0 的 AGENTS.md+vault 底座充分，地板效应），A1 成本更高；结构测试证实 Codex 不发现项目级 `.claude/skills/` 且其全局 `agent-task` 泄漏源自机器级控制包安装。owner 验收 No-Go 并关闭方向。

### Decision

项目级工作 Skill（trellium-work）不实现；`AGENTS.md + vault` 为既有项目接入的标准底座，Claude Code 直接读取 `AGENTS.md`，不再生成独立 `CLAUDE.md`；控制面保持用户级 `trellium`/`trellium-zh`；控制包模板源以不可发现文件名分发（AGENT_TASK_SKILL.template）。未来重开需 owner Level C 立项且以新的实证为准。

### Rationale

入口路由层不是 reviewer 深度的瓶颈；跨 Agent 的项目级发现位置缺乏可验证的一致机制。

### Impact

新项目接入只产出 AGENTS.md+vault，不为 Claude Code 复制第二份项目入口；不安装第二项目 Skill；`agent-task` 名称不再以可发现形态存在于发行包。

## D-0010 - Git 接入持久性 Gate（2026-09-18）

Status: Active

### Background

TASK-0013 确认 2026.09.7 存在接入假健康：`adopt` 生成完整协作层后核心未进 Git `HEAD`，fresh clone 全部丢失，`check` 仍报 0/0。owner 批准 Level C 立项并把"核心未进 HEAD"定为 error。P0/P1 预注册消融的正式裁决为 Inconclusive：P1 H3=1，未满足冻结 Gate 的 H1=H2=H3=0，因此不授权双语 Skill 候选契约；checker 与场景无关的 CLI 提醒独立修复。

### Decision

1. `adopt` 只输出场景无关的 `generated ≠ durable` 提醒与后续检查顺序，不声称本次生成文件的实际提交状态；双语 Skill 保持 P0，不加入未通过 Gate 的候选契约。
2. checker 以安装版本戳派生协作核心集合，机械核对 `HEAD`：当前 stamp 损坏报 `CORE_STORAGE_INVALID` error；未提交或 HEAD stamp 与当前协议版本/核心集合不相容报 `CORE_STORAGE_UNCOMMITTED` error；被 ignore 规则误伤报 `CORE_STORAGE_IGNORED` error；Git 验证命令失败报 `CORE_STORAGE_UNVERIFIED` error，非 Git 报同码 warning。local 模式以无写入 sentinel 验证边界（`LOCAL_BOUNDARY_UNCONFIGURED` warning / `LOCAL_BOUNDARY_OVERREACH` error / `LOCAL_BOUNDARY_UNVERIFIED` error）。checker 只读：不自动 `git add`/commit/push、不改 `.gitignore`、不运行 clone；fresh clone 是验收动作，不进入日常 check。
3. 版本控制动作永远归属用户：工具与 Agent 不得自动 commit/push。

### Rationale

场景 A 中 P1 的遗漏减少只是记录性收益；场景 B 中 P1 仍把 durable namespace 误归 local，违反冻结硬指标，不能据此增加长期 Skill 文本。机械 Gate 不依赖模型遵循，HEAD 事实与 fresh clone 可见性等价且成本低（M0 fixture 矩阵与 fresh-clone 对照冻结）。

### Impact

已 adopted 且核心未提交或当前 stamp 与 HEAD stamp 不相容的项目升级到 2026.09.8 后 `check` 从 0/0 转为 error——真实缺陷暴露而非回归，修复动作是用户提交完整一致的核心状态（本仓库 owner 未提交的 `docs/engineering/` 与 stamp 核心集合变化即真实样本）。Orion 升级与 fresh-clone 验收留给 TASK-0004。消融材料、投放偏差登记与逐格评分见 `docs/evals/adoption-durability-2026-09/`。

## D-0011 - 完整语言 Profile 的项目级持久化（2026-09-18）

Status: Active

### Background

TASK-0012 只把注释/API 规则持久化到项目；`init/protocol/profiles/go-backend.md` 的 module/workspace、分层、依赖、错误、资源、并发、HTTP、测试等完整工程知识仍只在首次控制 Skill 会话可见，后续普通会话会遗忘。Owner 明确裁定持久化能力必须交付，只消融载体。

### Decision

每个显式选择的 profile 生成独立完整项目文档 `docs/engineering/profiles/<profile>.md`，内嵌该 profile 的 roots；`AGENTS.md` 对工程任务一跳按当前路径与实际语言读取，不加载未匹配 profile。文件进入 adoption stamp 的 core 和 upgrade/diff 管理，profile metadata 记录 roots、完整源 hash、兼容注释规则路径与 `project_profile`。不自动猜语言，不写 Vault，不自动 Git add/commit/push。

中文发行模板由 canonical `init/protocol/profiles/*.md` 机械派生并做 byte-equality 防漂移；英文发行模板是同覆盖面的本地化派生，并由九类覆盖与真实 embedded-package adopt 测试约束。既有 `docs/engineering/code-comments.md` 作为 2026.09.7 兼容载体继续保留：迁移不删除、不覆盖定制，双方变化只出 proposal。

### Rationale

冻结消融要求压缩 capsule 先证明九类语义无损；当前没有该证据，因此 R1 淘汰并选择完整 profile。每语言一文件让多 root 共享同语言规则，同时防止多语言正文混用；把 12KB+ 工程规范放在条件路由目标而非默认 AGENTS/Vault，以文件复杂度换取按需 token。

### Impact

2026.09.8 的 legacy v2 profile 项目在 `upgrade --apply` 时新增完整 profile 文件；pristine 跟进上游，定制冲突走 proposal。未选 profile 输出集合不变。新增 profile 文件属于协作 core，必须进入 Git HEAD，fresh clone checker 才能通过。
