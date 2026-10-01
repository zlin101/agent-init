# TASK-0029 合并后的工作计划建议

## 基线与资料边界

- 2026-10-01 已切换到 `develop` 并执行 `git pull --ff-only origin develop`；本地与远端均为 `6a875d82227b65ab39978e4d281cbd26244c28ef`，拉取后工作区干净。该提交合并 PR #6，包含 TASK-0029。
- 本计划依据仓库归档的[定位讨论](2026-09-30-trellium-positioning.md)与[记忆边界复评](2026-09-30-memory-boundary-reassessment.md)。尚未确认 owner 所称“GPT 文档”是否另有所指；复评接收到的三层建议只到第三部分标题，不补写未提供的部分。
- 这两份文档保存 9 月 30 日的讨论现场；其中 D-0006 Active、存储尚未决定等描述是历史基线。当前已生效规则以 [D-0014](../../vault/decisions/D-0014-local-historical-evidence-store.md)及 canonical 协议为准。
- 本轮交付计划，不启动实现、不采纳新的治理规则。沿用 [TASK-0027](../../vault/tasks/TASK-0027-memory-boundary-reassessment.md)记录方案演进；TASK-0029 的接受不等于 TASK-0027 的方案已获接受。

## 已完成与仍待证明的部分

| 需求 | 当前结论 | 后续动作 |
| --- | --- | --- |
| local 历史移出工作仓后仍可找回 | TASK-0029 已 accepted 并合并；身份绑定、Store、成组保全、读回校验、失败保留来源已落地。 | 沿用现有规则，不重做存储方案。 |
| 历史与当前事实分开 | D-0014 明确历史默认不读、不授予 Authority、不作为 current truth；任务状态已有唯一 owner。 | 在实际接续中验证 Agent 是否正确使用这些边界。 |
| 功能的当前范围、理由、依据、缺陷和下一步容易找到 | 有 project/Decision/项目文档/runtime 等承载位置；复评 §4.6 指出闭合 TASK 不能永久代表 feature 当前事实。 | 优先检查路由、内容维护和证据关联，补具体缺口。 |
| 原有理由变化后仍能追溯 | 旧 Decision 与历轮 review 保留；Git 和 Store 承担各自范围的历史保存。 | 核对替代关系和历史出处是否易找，不预设所有 rationale 都要进 Store。 |
| 跨 Agent 接续能减少 owner 重复解释 | 定位讨论确认这是核心需求，但文本齐全并不能证明实际效果。 | 将一次实际功能接续作为下一任务的验收，不单独建设大型评估工程。 |

TASK-0029 的正式范围是 terminal local TASK 与对应 review ledger 的本机保全；不承诺跨设备、磁盘灾难恢复或完整会话采集。本仓仍为 tracked policy，本次拉取没有接入真实 `~/.trellium/history`。实现与历史验收见 [TASK-0029](../../vault/tasks/TASK-0029-local-historical-evidence-store.md)和[最终重审证据](../evals/historical-evidence-store-2026-10-rereview/batch4-RESULTS.md)。

## 推荐顺序

2026-10-01 最新 owner 指令为先梳理三模式现状，再决定是否及如何优化；依据见[Private / Local / Tracked 现状](2026-10-01-storage-modes-baseline.md)。以下优先级与 private 默认方向是待讨论建议，未启动实施或完成方案选择。

三模式与历史缺席理由梳理后，owner 明确同意“Private 不进项目 Git 与本机持久保全可以并存”。后续方案据此先收敛 Private TASK/review 的保全范围、稳定身份和找回/失败处置，再讨论切换默认模式；当前知识的恢复是另一项需求，不因 TASK 保全而宣称已解决。该回复确认方向，不自动扩大为整个 Vault 备份、实现授权或任务接受。

随后 owner 明确要求增加 Private History，已在独立 [TASK-0030](../../vault/tasks/TASK-0030-private-history-retention.md)推进实施；下述历史计划建议保留推理过程。默认切换仍未实施，TASK-0027 收尾与 tag-only 发布仍按其验收条件办理。

### 2026-10-01 新增方向：首次接入默认 private

Owner 表达“打算将 private 设置为默认模式”。暂按**产品首次接入的默认推荐与未指定时的选择**理解，已有项目保持原 policy，本仓仍为 tracked；这不是迁移本仓或已采纳新治理规则的指令。现行 [D-0012](../../vault/decisions/D-0012-local-default-task-storage.md)仍为 Active，待方案确定后再正式替代。

这会改变原计划的先后关系：先明确 private 的保全契约，再在这一边界下完善当前事实与接续。Private 当前不接入 D-0014 Store；全部 managed material 仅存在当前 clone，fresh clone 不提供恢复承诺。因此需区分两个问题：terminal TASK/review 的历史保全，以及 project/Decision/runtime 等当前知识的恢复。只把 TASK 写入 Store 不能替代当前知识的保存。

| 工作 | 最小范围与完成依据 |
| --- | --- |
| 明确保全边界 | 已询问 owner 是沿用 clone-only，还是仍需删除 clone 后可找回本机历史；若需要后者，还需定义当前知识及项目身份如何保存、定位和恢复，不预先指定数据库或新服务。 |
| 收敛默认接入契约 | 改为 private 默认推荐，保留显式 local/tracked；private 仍执行 preflight → adopt → policy/exclude → check。遇到 tracked carrier 继续零写入拒绝并给出其他模式选择，不静默切换、不自动 untrack。 |
| 核对安全与分发 | 使用现有 private 接入/forced-add 检测证据与回归；把此前记录的 private_preflight 损坏 Git metadata 分类纳入本任务评估。默认流程、文档和双语分发一致，既有升级不改变 policy。 |
| 完善接续 | 按选定的保全边界执行下方六问与实际接续核验；承诺 clone-independent 恢复时，须分别持有当前知识和历史的恢复证据。 |

实施为独立 Level C 任务，先冻结默认选择、保全范围、身份与失败处置。当前只记录意向和差距，不改现行规则、不新增恢复承诺。若 owner 明确选择沿用 clone-only，按该选择调整验收，保留其与原长期记忆目标之间的取舍说明。

### 第一优先：把当前功能事实与完成依据接起来

建议下一项实施工作聚焦“功能接续”，先以已交付的 History Store 为具体功能，检查新 Agent 从正式入口能否回答以下问题：

1. 当前能力的范围、调用路径和不支持的场景是什么？
2. 为什么采用当前设计，哪些旧判断已被替代？
3. 哪项任务在什么版本完成，依据是什么？
4. 哪些验证仍适用于当前版本，哪些仅能证明过去的验收？
5. 当前已知缺陷、未解决问题及其实际影响是什么？
6. 下一步应做什么，哪些行动仍需要 owner 授权？

逐项标注事实的现有 owner、入口和证据链接，只有找不到或相互矛盾的内容才补。功能行为继续由现有协议/API 文档负责，长期取舍由 Decision 负责，项目全局风险与下一步由 runtime 负责，TASK lifecycle 仍只在 TASK 中。索引只指路，避免复制全文和状态。

交付物应是必要的当前文档补齐、现有入口中的窄范围路由，以及收尾/后续修改时维护这些事实的具体步骤。仅在缺口确认后，才修改 canonical protocol、agent-task 或模板，并通过既有机制同步双语副本。先使用已有载体；可选长文档须符合现有 `details/` 的创建条件，不立即增加 Feature Registry、feature lifecycle 或 schema。

**验收标准：**上述六问都有明确出处；遗留问题进入当前 owner；任务 accepted 与“当前版本已验证”能够区分。若只有旧版本证据，明确标为尚未重新验证，不能继承旧 PASS。Owner 可以核对关键结论，无需重新口述整段任务历史。

### 第二优先：在同一任务中验证一次实际接续

在修改前冻结问题、正确出处和失败标准，再做最小调整与接续核验。使用隔离材料，不删除真实 TASK 或 Store；未参与实现的 Agent 从正常入口开始，记录回答、读取路径、错误和 owner 需要补充的内容。

| 场景 | 应有行为 |
| --- | --- |
| 正常接续，local TASK 不在 clone 中 | 能找到当前范围、理由、完成依据、遗留问题和下一步；正常判断不依赖展开全部历史。 |
| 任务已 accepted，但后来出现新缺陷或取舍 | 使用当前文档和新证据；保留历史 accepted 事件，不误报当前功能无缺陷。 |
| 按需追溯旧理由或 review | 找到来源及替代关系；历史内容不恢复旧 Authority，不覆盖当前约束。 |

通过标准是六问均可依据来源回答，且没有把历史当现行规则、把旧验收当新验证或越过授权的错误。若资料未覆盖问题，Agent 必须明确指出缺口。读取成本和 owner 补充次数作为辅助观察，不用 token 节省或关键词命中替代正确性。

这一次核验只证明该场景，不外推所有 Agent/CLI。已有文档加少量路由足够时就结束；失败后按入口未发现、记录遗漏、关联不清、内容过期、执行不遵从定位，再决定是否需要新增机制。后续有实际切换 CLI 的摩擦时，才追加相应场景。

### 第三优先：修复有证据的维护问题

独立排期，不与核心接续任务打包：

- **测试可靠性：**先处理 macOS 预存 ancestor-swap fixture，使全量回归重新成为可信的验收信号。最新 TASK-0029 验收为 258 tests、257 PASS / 1 预存 FAIL，不能称全量绿；本轮没有重跑这组测试。
- **Store 的两项 P3 residual：**非目录条目分类与大小写不敏感文件系统上的通用 artifact id 冲突仍披露在 [review 台账](../../vault/tasks/TASK-0029-review.md)。出现通用调用方或对应真实风险时，再立限定修复任务；不重开已接受任务。
- **其他已记录的窄缺口：**`private_preflight` 的损坏 Git metadata 分类留待 private 接入场景评估；TASK README 的旧 runtime projection 文案作为文档 drift 单独修正。它们不自动扩大本次计划实施范围。

## 现在不作为主线的方向

跨设备备份、旧资料批量回填、完整聊天/tool trace 采集、数据库/图谱/向量检索、新 history CLI、自动 cleanup、跨项目经验系统均没有成为本轮必要步骤。未来只在具体使用需求和失败证据出现后，另立任务核对隐私、持久性与维护成本。已关闭的 context/review-pack/Skill 方向不因三层术语再次开启。

Owner 于 2026-10-01 明确计划在 TASK-0027 结束后发布新 tag，继续遵循 tag-only。当前 TASK-0027 的 owner_review 仍 pending；收尾时先确认最终交付范围、版本与目标提交，再完成发布检查及 tag 操作。本轮不提前打 tag，也不把未实施的 private 默认或 private retention 写入发布内容。接入真实 local 项目、回填历史或清理来源仍遵循各自授权，拉取合并代码本身不触发这些操作。

## 下一任务的建议契约

- **目标：**新 Agent 能从现有入口理解 History Store 的当前事实、取舍、完成依据和遗留问题，并正确按需追溯历史。
- **范围：**六问差距核对、必要的现有文档/路由补齐、确认缺口后的最小收尾规则与双语同步、隔离接续验证及证据记录。
- **不做：**Store 重写、新 schema/CLI/Feature Registry、真实资料迁移或清理、扩大文件系统保证、commit/push/tag。
- **任务等级：**若涉及治理规则或外部契约，为 Level C；下一实施任务须冻结实际修改范围。本计划不启动该任务。
- **停止条件：**既有载体与最小路由满足六问及接续边界后结束；新增载体需独立说明现有机制无法解决的具体失败。

## 本轮检查

本轮只更新计划、TASK-0027 分析记录及 runtime 的过期导航。拉取后已执行 sync-skills、check、status；文档落盘后的链接、whitespace、仓库健康与状态检查结果记录在 TASK-0027。本轮未执行上述接续实验，不将计划中的验收标准标记为通过。
