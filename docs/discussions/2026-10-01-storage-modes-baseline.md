# Private、Local、Tracked 三种存储模式现状

## 范围与基线

Owner 要求先梳理追踪、忽略、边界和管理，再决定是否及如何优化。“Tracet”暂按现有模式 `tracked` 理解。本文件只描述现状与待讨论边界，不修改默认值、迁移模式或采纳优化方案。

后续实施说明：Owner 在完成本次基线梳理后明确要求 Private History，工作区扩展由 [TASK-0030](../../vault/tasks/TASK-0030-private-history-retention.md)与 [D-0015](../../vault/decisions/D-0015-private-historical-retention.md)承载。下方表格保留 6a875d8 时点的 Private 不触发 History 的原始分析，不代表扩展后的规则；当前规则请读上述记录及 canonical 协议。

基线为 develop `6a875d82227b65ab39978e4d281cbd26244c28ef`，已包含 TASK-0029。现行 Skill 首次接入推荐/默认 `local`；本仓 policy 仍为 legacy v1 `task_storage=tracked`。新 policy 使用 v2 `storage_mode=tracked|local|private`；旧 v1 tracked/local 可解析，升级不自动改写。

“默认 local”属于 Agent/Skill 工作流：先选模式，adopt 后写 policy。当前原始 index 模板仍为 v2 tracked；单独运行裸 adopt 不等于已配置 local。没有 CLI storage 参数，日常 checker 以项目实际 policy 为准，不补隐藏默认值。

这里讨论**接入目标项目**的 Trellium 文件，不是将 Trellium 产品仓库自己的 `scripts/`、`init/`、分发源码隐藏。业务文件和项目自有 Git 规则由项目管理；安装在用户目录的 Trellium Skill、缓存也不由目标 policy 决定。

主要依据：[Vault 协议](../../init/protocol/10-vault.md)、[接入协议](../../init/protocol/70-adoption-flow.md)、[双语分发中的中文 Skill](../../skills/trellium-zh/SKILL.md)、[检查与升级实现](../../scripts/trellium.py)、[D-0012](../../vault/decisions/D-0012-local-default-task-storage.md)、[D-0014](../../vault/decisions/D-0014-local-historical-evidence-store.md)。

## 1. 哪些文件追踪，哪些忽略

下表的“进 Git”是模式要求或预期，**不代表脚本自动执行 add/commit/push**。生成、加入 index、提交到 HEAD、推送远端是不同步骤。协作核心的具体清单从 `vault/.agent-init.json` 的合法 files inventory 加 stamp 自身派生；表中展示典型安装路径。

| 文件/内容 | Private | Local | Tracked |
| --- | --- | --- | --- |
| `AGENTS.md` | 整个文件忽略、不追踪 | 进 Git，保留项目原有内容和 Trellium 标记区块 | 同 Local |
| `vault/index.md`、`governance.md` | 忽略、不追踪 | 进 Git | 进 Git |
| `vault/project.md`、`runtime.md`、`collaboration.md` | 忽略、不追踪 | 进 Git | 进 Git |
| `vault/decisions.md`、`decisions/`、`details/` | 整个 Vault 命名空间忽略 | 保留在 Git 中，不应被任务忽略规则误伤 | 保留在 Git 中 |
| `vault/handoff.md`、`parked.md` | 忽略、不追踪 | 进 Git；内容维护仍遵循 handoff/parked 规则 | 同 Local |
| `vault/tasks/README.md` | 忽略、不追踪 | 进 Git，不能随任务日志一起忽略 | 进 Git |
| `vault/tasks/TASK-*.md` | 忽略、不追踪 | 忽略、不追踪 | 任务流水进入 Git |
| `vault/tasks/*-review.md` | 忽略、不追踪 | 忽略、不追踪 | 纳入完整任务流水的 Git 保存范围 |
| `vault/tasks/archive/` | 忽略、不追踪 | 忽略、不追踪 | archive 文件进入 Git |
| `vault/tasks/.gitignore` | 若存在，随 Vault 忽略 | 作为共享忽略规则进 Git | 首次 tracked 接入不添加 local 的任务忽略规则 |
| `skills/agent-task/` | 整个目录忽略 | 安装的协作工作流进 Git | 同 Local |
| `docs/engineering/code-comments.md`、已选 `profiles/*.md` | 安装/登记的具体路径忽略 | 进 Git | 进 Git |
| `vault/.agent-init.json` 安装版本戳 | 忽略、不追踪 | 进 Git，参与接入持久性校验 | 同 Local |
| `vault/project-id` | 首次接入不创建 | 首次启用历史保全时创建/校验，**tracked** | 首次接入不创建 |
| `vault/.upgrade/` 升级冲突提案 | 随整个 Vault 忽略 | 不在任务忽略范围内；由升级评审/项目 Git 流程管理 | 同 Local |
| `.agent-init-backup/` | 在 private 固定忽略范围内 | 不由 local 的任务忽略规则处理 | 不由 tracked 模式统一指定忽略规则 |
| 业务源码、测试、CI、依赖、其他项目文档 | 沿用项目规则 | 沿用项目规则 | 沿用项目规则 |

三种模式都不按文件中的“相关文字”扫描或判断隐私。Private 的固定边界是 `AGENTS.md`、整个 `vault/`、`skills/agent-task/`、`.agent-init-backup/`，外加合法 stamp 登记的其他具体 managed paths。例如 `docs/evals/` 下另存的原始输出、任意 `docs/` 文件或额外工具入口，不会因为内容谈到 Trellium 就自动被 private 忽略。额外 carrier 若需要纳入，应明确其管理身份，不能假设已覆盖。

特别注意：把某个项目文件放入 `vault/` 或 `skills/agent-task/`，就会受到 private 对整个命名空间的忽略。Private 不使用 `/docs/`、`/skills/` 之类扩大到无关内容的规则。

## 2. 忽略规则在哪里

### Private

Agent 在 Git 定位出的 `info/exclude` 文件维护 `trellium-private` 标记块。常规仓库显示为 `.git/info/exclude`；实际路径通过 `git rev-parse --git-path info/exclude` 获取，不假设 `.git` 一定是目录。

目标位于仓库根目录时，固定规则为：

```gitignore
# trellium-private:start .
/AGENTS.md
/vault/
/skills/agent-task/
/.agent-init-backup/
# trellium-private:end .
```

有已登记工程文档时，在块内追加它们的精确 anchored 路径，例如 `/docs/engineering/code-comments.md`、`/docs/engineering/profiles/python-backend.md`。monorepo 的规则带目标前缀，例如 `/packages/api/vault/`，不能影响邻近项目。上面的最小块不能代替包含 extras 的项目完整块。

该配置属于 Git 本地管理资料，不进入项目提交。目标标记必须完整、唯一、与路径匹配；规则不能扩大边界，也不能被其他规则取消忽略。

### Local

Agent 创建目标项目中的 `vault/tasks/.gitignore`：

```gitignore
TASK-*.md
*-review.md
archive/
```

这份 `.gitignore` 本身应进 Git，使 fresh clone 继续采用同样的日志边界。不能用 `/vault/` 一并隐藏当前知识、任务 README、决策和细节文档。

### Tracked

不因该模式添加 TASK/review/archive 忽略规则；这些文件应按项目流程纳入 Git。它也不会自动取消已有 ignore，或替用户提交文件。模式与已有 Git 状态冲突时，要处理冲突，不能仅改 policy 后宣称迁移完成。

## 3. 各自边界与恢复承诺

| 维度 | Private | Local | Tracked |
| --- | --- | --- | --- |
| 仓库可见性 | managed 协作层全部不进 Git | 协作核心/当前知识进 Git；TASK/review/archive 不进 Git | 协作核心和完整任务流水进 Git |
| fresh clone | 不包含原 clone 的 Trellium 协作层 | 包含已提交核心与当前知识，不包含本地任务日志 | 包含已提交核心与任务流水 |
| 当前知识的持久化 | 留在当前 clone，无内建跨 clone 恢复承诺 | 已提交版本通过 Git 保存 | 已提交版本通过 Git 保存 |
| terminal TASK/review 的外部保全 | **不触发** | 写入本机 Store 并读回验证 | 不触发，按 Git 流程保存 |
| `vault/project-id` | 无本模式身份接入流程 | tracked UUID，唯一 canonical 身份 owner | 无本模式身份接入流程 |
| clone 删除后的历史找回 | 无模式内保证 | 仅已成功保全的 TASK/review 可按身份与 artifact 找回 | 需存在保留下来的 Git 副本/远端，且相关内容已提交 |
| 未闭合任务/现场 | 没有自动外存备份 | terminal retention 不备份仍 active 的任务、现场或全部 Vault | 未提交资料不会因模式名而获得 Git 恢复能力 |

Local 的 Store 默认在 `~/.trellium/history`，保存 TASK 与必要 ledger 的原始内容、SHA-256 版本及有限 metadata。它不保存整个项目、当前 Vault、链接指向的 CI/日志内容，也不承诺跨机器或磁盘故障恢复。

找回历史不等于恢复当前任务或授权。历史默认不读、不取代 current truth、不继承旧 Authority；后续工作须依据当前入口和任务契约。

Private 是 Git 可见性配置与机械检测边界，不是加密、访问控制、历史擦除或绝对防上传。Ignored 文件仍可被 Agent 读取，用户也能用 `git add -f` 强制加入 index；checker 会报违规，但不会拦截 Git 命令或回滚上传。已存在于旧 Git 提交中的内容不会被 ignore 清除。

## 4. 如何管理

### 接入与验收

| 模式 | Agent/owner 流程 | checker 实际职责 |
| --- | --- | --- |
| Private | adopt 前运行只读 `private_preflight`；通过后 adopt、写 v2 private policy、维护 exclude block、运行 check。候选路径已有 tracked/HEAD 副本时拒绝，不能只忽略 AGENTS 的局部区块。 | 检查固定 namespace 与 stamp extras 不在 index/HEAD；标记块及忽略效果正确；强制 add 可被发现。没有 Git 时报告未验证 warning。 |
| Local | adopt、写 local policy、窄范围 TASK ignore、完成 project-id 绑定与 inventory 登记；owner 控制核心 Git 提交，再 check 和一次 fresh-clone 接入验证。 | 核心路径必须在 HEAD 且不被忽略；TASK/review/archive 不得 tracked/staged；未来日志须被忽略，durable namespace 不得误伤。 |
| Tracked | adopt、确定 tracked policy；owner 控制核心及任务提交，运行 check。 | 核心路径在 HEAD 且不被忽略；任务不得 ignored；已闭合 TASK 和 archive 须在 index；尚未追踪的 open TASK 报 pending warning，index 已知但工作树缺失的 TASK 报 error。 |

检查力度并非每类文件完全相同：核心使用 HEAD 持久性 Gate；任务状态规则主要检查 index。当前 tracked 的 review ledger 会检查忽略冲突，但没有与 closed TASK 完全相同的“未追踪即 error”门。因此 check 通过不能替代对完整 review 流水是否已提交的核对。

Local 的 `LOCAL_BOUNDARY_UNCONFIGURED` 是 warning，durable overreach 是 error；Private 的缺配置、规则越界、已追踪或无法验证等在 Git 项目中通常是 error。两者不能用同一种“0 error 就已保证所有内容保存”的解释。

Private preflight 的“非仓库”判定仍含此前记录的 stderr 分类分支，损坏 Git metadata 场景尚待独立评估；本文件没有把该路径评估或修复标记为完成。

### 开发、收尾与历史

所有模式使用相同的 TASK lifecycle，状态由 TASK 自己持有；runtime 不成为第二任务状态面。历史 ledger 保留原路径，收敛结论可以进入 TASK Execution Record。

- **Private：**采用 local lifecycle 的知识处置 gate。完成前填写 `none — 理由` 或 `distilled — canonical 目标文件`；蒸馏出的 Decision 等仍在 ignored 的 Vault 中，不会因“canonical”而公开。没有后续 Store retention 步骤。
- **Local：**同样完成知识处置；长期结论进入 Git 中的 canonical 文件。terminal 后 TASK 与必要 ledger 成组分别 put/get，全部验证成功才算 retention 完成；部分失败保留来源、可重试，accepted 不回滚。成功后也不自动删除来源。
- **Tracked：**知识处置默认 `not_applicable`，仍需维护适用的项目知识；完整任务材料按 Git 流程保存。不自动调用 Store。

知识处置和 retention 都含 Agent 执行及人工核对，`trellium check` 不会自动执行 Store 写入，也不会验证自然语言结论是否充分或实际 retention 是否完成。`none` 只说明没有新长期知识，不允许省略 local 历史保全。

### 升级与迁移

三种模式都用本地 stamp 记录安装版本、文件 inventory 与 hash。数据文件（project/runtime/decisions/tasks 等）由 Agent/owner 维护，升级器不拿模板覆盖；协议载体可安全更新，本地与上游同时变化时生成 `vault/.upgrade/<version>/` 提案，由 Agent/owner 处理。

Private 的升级提示是保持 untracked/ignored 并复查；Local/Tracked 的升级结果走项目 Git 提交流程。脚本不会自行操作 Git index、commit、push；不会使用 skip-worktree、assume-unchanged、hook 或全局 exclude 来隐藏冲突。重复 adopt/upgrade 保留原模式，切换模式需要单独评审，不能自动 untrack。

## 5. 为什么 Private 没有接入 History

Owner 进一步询问这一差异的出发点。现有记录支持以下区分：

1. **原始产品定位：**2026-09-28 的 [Private 实施计划](../superpowers/plans/2026-09-28-private-storage-mode-plan.md)定义其用途为个人使用时不让目标仓库出现任何 managed material，承诺 Git 配置边界与机械检测；§4.2 明确把跨 clone 恢复和团队共享列为非目标。因此最初只交付当前 worktree 内的协作能力。
2. **后续实施范围：**2026-09-30 的 [TASK-0029](../../vault/tasks/TASK-0029-local-historical-evidence-store.md)将 local terminal TASK/review 保全作为目标，明确排除 private retention/privacy 语义。D-0014 同样保持 tracked/private 不变。这是已冻结的交付边界，不是对 private 保全方案的否决。
3. **现有接入依赖：**Local 的项目身份是 tracked `vault/project-id`，由 Git 与 stamp 的绑定证据保护。Private 要求 managed material 全部不进 Git，不能原样继承这一身份持久性契约；外部保存哪些内容、身份怎样稳定保存与找回、删除 clone 后怎样恢复尚未为 private 定义和验证。

从任务顺序与冻结范围看，先完成当时默认 local 的具体缺口、保持 private 原有语义是分阶段交付的取舍；这是依据记录作出的解释，不能补写成“已经证明 private 不需要保全”。记录没有证明 private 在技术上不能使用 Store，也没有证明本机 clone 外保存违背“不进入项目 Git”的需求。

当前判断是：不进 Git与是否持久保全可以分开；private 的 clone-only 是已有范围选择，不是私有性必然要求。若目标改为 private 默认并长期接续，原范围值得重新评估，但本轮不据此直接扩展实现或恢复承诺。

Owner 随后明确回复“同意”，确认上述方向：Private 的 Git 可见性与本机持久保全可以并存，不能仅凭 Private 模式名排除历史保全。该共识不等于已切换默认模式、已确定 private 身份/恢复方案或已授权开发；三种模式的现行行为仍按上文执行。

## 6. 本次梳理后留给讨论的问题

现状已区分仓库可见性、知识维护和历史保全三个维度。下一步是否优化，由 owner 在此基线上决定，先不选择实现：

- Private 是否继续 clone-only，还是需要当前知识与历史各自的外部保全？
- 三种模式的完整 review 提交/retention 证据，应继续人工核对还是需要更强的检查？
- 是否调整首次接入的推荐/default，以及 tracked carrier 冲突时的用户选择？

本轮做协议与源码核对、文档落盘及健康检查，没有迁移真实项目、改产品代码或执行新的模式行为测试。
