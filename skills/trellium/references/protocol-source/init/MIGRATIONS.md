# Migrations 迁移手册

本文件是升级机制的数据保护手册：每次协议模板变更，逐条写清旧内容的去向，供执行升级的 Agent 读取。当前版本号见 `init/VERSION`；升级机制与保护边界见 `init/protocol/70-adoption-flow.md`。

条目格式：

- `Added` / `Removed` / `Breaking` / `Auto`：模板与文件层面的机械变化，由 `trellium.py diff` 报告、`upgrade --apply` 执行；
- `Agent migration`：需要 Agent 语义执行、用户确认的迁移动作。数据文件（runtime、handoff、decisions 等）的格式迁移一律属于此类：只做内容搬运，不丢事实，不做"判断不重要然后丢弃"。

## 2026.10.1 — Trellium Work rename

- Changed: 现有项目 starter workflow `agent-task` 更名为 `trellium-work`，标题 `Trellium Work`，新项目唯一目标为 `skills/trellium-work/SKILL.md`。安装/接入包仍叫 `trellium` / `trellium-zh`，不增加新的 Agent 发现位置或第二入口。双语模板以不可发现名称 `TRELLIUM_WORK_SKILL.template` 分发。
- Fixed: 安装包 UI 显示名称同步为 Trellium / Trellium 中文版，default_prompt 分别调用实际 `$trellium` / `$trellium-zh`，不再引用旧 agent-native-init 名称；安装位置和工作内容不变。
- Compatibility: 旧 `skills/agent-task/SKILL.md` stamp 条目仍为有限 allowlist 中的 template，旧 Private block 仍可只读 check。含旧文件或旧 stamp 绑定时，adopt（包括 --force）、upgrade（包括 --complete）以及无 stamp 的 baseline 在写入前拒绝，提示显式迁移；不自动 add/remove 两份工作流。
- Agent migration: owner 确认后先核对旧文件和 stamp，使用原版本工具完成已有 pending proposal 的旧轮；新路径已有文件、旧文件丢失/非普通文件或 stamp 非法时先解决冲突/恢复，不覆盖、不补写空模板。将旧 SKILL.md 移到不存在的新路径，保留全部定制，仅更新 frontmatter `name: trellium-work`、标题和实际相关引用；旧位置不再留 SKILL.md。
- Agent migration: stamp 存在时仅将 files 中旧路径的 template 条目改为新路径，baseline 记录迁移后文件 SHA-256，并标记 observed=true；保留 entry 的兼容信息、其他 files 条目、project-id、protocol_version、profiles 和全部其他 stamp 字段。stamp 不存在时，移动并确认名称后运行 baseline，走 unversioned proposal 保护；不得通过重跑 adopt 覆盖已有数据。对已有 pending proposal 的迁移需先完成旧轮，不携带悬空的 proposal 路径。
- Agent migration: Private 同步将精确 `trellium-private` block 的 `/skills/agent-task/` 改为 `/skills/trellium-work/`（monorepo 保留原 prefix），保持其他边界不变；读回 check 0 errors 后再调用 identity/upgrade。Local/Tracked 由 owner 授权提交路径和 stamp 的协调变更，未提交时 HEAD Gate 如实报错；工具不执行 Git 操作。现有旧 namespace 的其他文件由 owner 按用途处置，Private 不允许将残余旧内容强制 add。
- Verification: 完成迁移后运行 diff、按 proposal 保留定制，必要时 upgrade --complete，再 check。用户级已安装 Skill 不由项目迁移改写；需用户按现有安装方式更新包。历史讨论和已接受任务中的旧名称不回溯改写。

## 2026.10.0 — private historical retention

- Changed: Private terminal TASK/review 也执行现有本机 History Store 的成组 put/get 保全；所有目标 managed material 仍不进 Git，默认仍 Local。Store 路径/格式/API 与知识处置、失败保留来源/重试、非 Authority 边界不变，不增加同步或当前 Vault 备份。
- Changed: ensure_project_identity 接受显式 local/private policy；Private 在写入前验证有效 stamp 与 Git/private 边界，vault/project-id 随 Vault ignored，登记 data role，已登记 UUID 改变或丢失时拒绝替换。Local 的 tracked 身份不变；HEAD 路径有无改用 ls-tree 的结构结果，不再解释 cat-file 的“文件只在工作树”错误文本。
- Fixed: Private preflight 不再仅凭 not-a-repository stderr 放行，须结构证明祖先没有 .git；损坏 HEAD/ref、未知 Git 证据和 prefix 查询失败拒绝。Private checker 同样将既有 metadata 的查询失败报告为 error，普通非仓库仍为 warning。
- Agent migration: 存量 Private 启用时由 owner 确认首次绑定或恢复已知原 UUID；不自动回填历史、不清理 source、不自动切换模式或写 Git index。新 Private clone 先完成接入/ignore，再按已知 UUID/artifact/digest get 核对历史，恢复原 UUID 文件并运行 helper 复用登记；原 UUID 丢失时不猜项目、不将新绑定当旧历史。跨机器需要自行迁移 Store 与身份，没有自动同步。协议与实际命令见分发 Skill。

## 2026.10.0 — local historical evidence store

- Added: bundled identity helper `ensure_project_identity(target, authorize_create=...)`（不注册 CLI）：仅在显式 local policy 下执行；复用并严格校验 `vault/project-id`，已有绑定证据（版本戳 inventory 或 Git HEAD）而文件缺失时要求恢复，仅授权的首次绑定可创建，创建后登记失败保留身份文件、重试复用同一 UUID；以既有 `data` role 登记进版本戳 files inventory（既有 schema，不复制 UUID 值）。该路径加入 stamp 管理集，沿用现有 Git durability 检查保护；重复 adopt/baseline/upgrade 保留登记条目，upgrade 永不提案、创建或改写该文件。
- Added: 正式历史证据模块 `scripts/history_store.py`（标准库、Python ≥ 3.9、无 CLI）：put/get/list + 最小 `retain_terminal` 适配，原子目录发布、per-artifact flock、SHA-256 不可变版本、fail-closed 完整性读取；经 sync-skills 以 `assets/history_store.py` 分发并纳入 drift 检查；现有安装方式可直接调用，无新增依赖。
- Changed: review 台账收敛后不再删除——结论归档进 TASK Execution Record，原台账文件保留在原路径作为历史载体；local 任务 terminal 时 TASK 与已开展 review 的台账成组写入本机 Store 并逐份 get 验证，整组成功才算 retention 完成；失败保留 source、不回滚 accepted、幂等重试；默认不 cleanup。canonical 依据见 `10-vault.md`「Historical Evidence 保留（local）」与 `20-governance.md` 验收门。
- Agent migration: 存量项目不自动回填——local 接入按 policy → 身份 helper → check 顺序接入；既有 terminal local TASK 仅在 owner 授权后回填，不批量删除、不宣称丢失材料可恢复；D-0006 由新 decision 显式 superseded，原 reasoning 保留；本仓 `vault/collaboration.md` 中与「可丢弃」直接冲突的现行表述由 Agent 按 D-0014 更新，历史观察记录不改写。

## 2026.10.0 — hot-path routing ablation (Round 3)

- Changed: entry-reading contract single-sourced in `30-agent-entry.md`; `10-vault.md` no longer restates the default-read flow (points at 30; storage/information duties kept); `80-execution-patterns.md`, `40-skills.md`, the `agent-task` Skill (repo copy + bilingual templates) and bilingual `protocol-model` references now delegate context reading to the project `AGENTS.md` entry instead of prescribing their own pre-read group.
- Removed: the standalone `## 默认读取` / `## Default Reading` section from `vault/index.md` and both index templates, plus update-rule bullets duplicated from AGENTS/governance. Kept verbatim: `trellium-policy` block, task/authority cheat sheet, file-responsibility and detail-routing catalog, policy-related update rules (local/private storage contract, budget single-source).
- Unchanged: `AGENTS.md`/bilingual templates and `agent_entry_section()` read sets (the S2 Level A index-skip candidate was killed by kill-gate evidence; no light-read behavior change for existing projects), markers, three-way profile routing, customization/proposal protection, upgrade and data semantics; runtime/project/data remain script-read-only data surfaces. The local `vault/runtime.md` present-tense trim is a manual Agent data move with cold provenance recorded in TASK-0028; no runtime template changed.

## 2026.10.0 — profile knowledge ablation (Round 2)

- Changed: Go/Python canonical profiles and English templates ablated of teaching payload (command tutorials, directory skeletons, code examples, basic-syntax facts); decision constraints, risk constraints, toolchain/stack preferences, local-contract-first and no-config fallbacks are preserved. File paths, roots, CLI, stamp schema, routing, Comment ownership, upgrade/proposal/storage semantics unchanged; customization protection unchanged (existing local profile edits still take the upgrade proposal path).

## 2026.09.10 — private storage mode

- Added: policy schema v2 `storage_mode`（`tracked | local | private`；默认 local）与 legacy v1 `task_storage` normalization；既有 v1 policy 不自动改写。
- Added: `storage_mode=private` 反向 privacy Gate——managed material 必须 untracked 且被 `.git/info/exclude` 的 canonical `trellium-private` block 精确忽略；`PRIVATE_STORAGE_TRACKED`（含 `git add -f`）、`PRIVATE_STORAGE_UNCONFIGURED`（block 缺失/畸形/重复，或按实际 `git check-ignore` 结果未被 ignore，包括后置 negation）、`PRIVATE_STORAGE_OVERREACH`、`PRIVATE_STORAGE_UNVERIFIED`（Git 查询失败、缺 stamp、stamp 声明的唯一副本缺失或非普通文件）全部 error fail-closed；非 Git 目标为 warning。
- Added: 只读探针 `private_preflight(target, profiles)`——adopt 之前由 Agent 调用（bundled 脚本内加载），任一候选 managed path 已 tracked/in HEAD 即拒绝；Git 查询失败 fail-closed；探针零写入。不新增 CLI。
- Changed: Private 模式下 upgrade 的 untracked managed 文件不再视为 dirty；无冲突完成提示改为保持 untracked/ignored 并重跑 check，不提示 commit；diff/upgrade/proposal 依旧零 Git 写入。
- Agent migration: 既有 tracked/local 项目不自动迁移；Private 接入是 Agent-native 显式流程（preflight → adopt → private policy → exclude block → check）。tracked AGENTS 与 private 冲突时 preflight 拒绝并给出 local 退路。

## 2026.09.10 — Profile 路由 conformance

- Fixed: 既有 `AGENTS.md` 上追加的 Trellium 入口从只路由 `docs/engineering/code-comments.md` 修正为同时按 root 与实际语言路由完整 `docs/engineering/profiles/<profile>.md`，与 D-0011 及新项目模板路由一致；重叠注释/API 规则仍以兼容载体为项目定制优先。CLI、文件布局、Profile 内容、stamp schema 与 merge/overwrite/proposal 行为均不变。
- Auto: 双语嵌入脚本与 generated snapshots 同步为对齐后的路由语义。

## 2026.09.10 — risk-first 任务分级

- Breaking: 未来任务分级改为 canonical 三步流程——命中 Level C 风险域 → C；否则中断恢复或协作成本明显较高 → B；否则 → A。删除“涉及 2 个以上文件”“验收标准超过 3 条”“1-2 个文件”等单一规模充分条件：规模只可提示进一步判断，不能单独决定等级。Level C 风险域为安全/隐私、公开 API 或外部契约、持久数据/迁移、部署/生产行为、依赖变更、实质成本/配额、架构方向/重大架构决策、治理规则/策略；一行高风险修改也可能是 C。不因任务后来意外跨 session 或中断而回溯改写历史任务分级。
- Auto: 双语 governance/index/agent-task 模板、`protocol-model.md` 简明引用与 generated snapshots 同步为 risk-first 语义。无 schema、checker、finding、评分或 API 变化：分级仍是 Agent 语义判断，不进入工具校验。
- Agent migration: `vault/governance.md` 与 `vault/index.md` 是 merge 角色的 protocol 载体：pristine 文件升级时自动刷新为 risk-first 语义；定制过的文件不被覆盖，而是生成 proposal，由 Agent 按提案人工把本地 Task Levels 与速查表中的规模阈值替换为三步流程语义；`trellium-policy` 策略块等用户数据保留。历史 TASK 文件与既有 runtime 记录不回溯重分类。

## 2026.09.10 — budget health decoupling

- Breaking: `BUDGET_EXCEEDED`（热文件预算与 `max_active_tasks`）从 correctness `error` 降为仓库健康 `warning`：仅有 budget warning 时 `check`、`status` 与 CI 直调均退出 `0`；普通业务任务不因预算超出而无法验收。finding code、消息、measurement schema 与 policy 字段不变。结构/规范化损坏仍是 error（exit `2`）：`POLICY_INVALID`、`TASK_STATE_INVALID`、`FILE_UNREADABLE`、symlink/non-regular canonical 输入与 storage 安全契约损坏（`CORE_STORAGE_*` error 态）；而 `POLICY_MISSING`、legacy `TASK_STATE_MISSING`、`REQUIRED_FILE_MISSING` 本就是 warning，不变。
- Removed: AGENTS、agent-task Skill、Vault routing 与 compaction protocol 中“任务收尾超预算即自动五阶段压缩”的默认耦合；预算超出只报告为健康信号，不自动扩大当前 TASK scope、不产生额外提交。
- Auto: 新接入项目的双语 AGENTS/index/agent-task 模板与 generated snapshots 同步为 warning 语义；显式 compaction 能力（五阶段、安全边界、独立提交）原样保留。
- Agent migration: `vault/index.md` 的 `trellium-policy` 策略块是 protected data，不由升级脚本覆盖。升级时人工删除项目内“超预算即收尾压缩”类规则，改为“报告 warning；仅在用户显式要求、独立 maintenance TASK、任务契约明确包含或热文件结构损坏需要恢复时执行压缩”。已有压缩流程与算法不变。

## 2026.09.10 — handoff 收敛为 transient delta

- Changed: handoff 契约收敛为三小节（`Why interrupted` / `Transient context not captured elsewhere` / `Exact resume point`）；旧七字段（Objective/Completed/In Progress/Failed Attempts/Blockers/Next Best Action/Files To Read First）全部废除，其内容不再有任何持久化副本义务。写入触发改为双重条件：真实中断 + 存在无法从 canonical 状态（TASK/Git/工作区/重跑测试/durable knowledge）低成本推导的恢复事实。
- Removed: 模板中示例 `## TASK-` / `## SESSION` 标题全部移除（预算计数器会把它们算成真实条目）；空模板必须测得 `handoff.entries == 0`。普通完成、等待 acceptance、完成 review、open lifecycle 不再触发 handoff。
- Auto: 新接入项目的双语 handoff 模板为空模板态（零可数条目、仅记载三小节形态）；protocol、Skill、concise references 与 generated snapshots 同步为 transient-delta 语义；恢复顺序固定 TASK → Git/工作区/测试 → handoff delta。
- Agent migration: `vault/handoff.md` 是 protected data，不由升级脚本覆盖。升级时对每条现有 handoff 做三分法判定，禁止整段搬运：(1) 完全可从 canonical 状态推导 → 直接删除；(2) 含唯一 durable 事实（长期约束、安全边界、失败结论）→ 先以最短形式蒸馏进 TASK Execution Record 或 decision，再删除条目——只搬结论一句，不搬叙述、进展或测试历史；(3) 含非可推导 transient delta → 改写为三小节保留，消费后删除。历史 Git 版本与已归档任务不回溯迁移。

## 2026.09.10 — 删除 runtime TASK projection

- Breaking: `trellium-task-state` 状态块成为 lifecycle、Authority、slice 与 Gates 的唯一持久化 owner；`runtime.md` 不再保存 Active Tasks 表。Focus 可保留，但只有导航语义，指向不存在的 TASK 时只显示 navigation unresolved，不使 TASK lifecycle unresolved。
- Removed: `check` 删除 `TASK_PROJECTION_MISSING`、`TASK_RUNTIME_CLOSED_LOCAL`、`TASK_RUNTIME_DRIFT`、`TASK_RUNTIME_DUPLICATE`、`TASK_RUNTIME_INVALID`、`TASK_RUNTIME_LOCAL_UNRESOLVED`、`TASK_RUNTIME_MISSING`、`TASK_RUNTIME_UNRESOLVED`。`status` 直接扫描 TASK 状态块，JSON 不再输出 `runtime_projection`，文本不再输出 runtime objective/next action。
- Added: tracked storage 用 Git index 只读识别“已索引 TASK 文件在 working tree 中缺失”，并沿用 `TASK_STORAGE_MISMATCH`；不从 Git 历史重建 inventory，不为 local/private 提供恢复承诺。
- Auto: 新接入项目的双语 runtime 模板不再生成 Active Tasks 表；protocol、Skill 与 generated snapshots 同步为 canonical task-state 语义。
- Agent migration: `runtime.md` 是 protected data，不由升级脚本覆盖。升级时人工删除 Active Tasks 表，保留 project-global runtime 事实与可选 Focus；不把 objective/next action 搬入状态块，不扩展 schema。local/private TASK 在 fresh clone 中消失仍属于 storage contract。

## 2026.09.9 — 首次接入默认 local TASK storage

- Changed: Skill/Agent 首次接入前询问 owner 选择 TASK storage，推荐 `local`；owner 未指定时按 local 执行。需要共享完整任务流水时选择 `tracked`。这不新增 CLI 参数或交互式脚本流程。
- Added: Agent 在 local 接入时创建 `vault/tasks/.gitignore`，规则仅覆盖 `TASK-*.md`、`*-review.md` 与 `archive/`；协作核心仍进入 Git。tracked 接入不添加这些 ignore 规则。
- Safety: 重复接入与升级保持既有 policy，不因新默认静默切换 storage。
- Agent migration: 既有项目不自动迁移、不自动 untrack，也不改项目根 `.gitignore`。若 owner 决定在 tracked/local 间切换，需单独评审 policy、窄范围 ignore 规则和 Git index 变更后再执行。

## 2026.09.8 — 接入持久性 Gate 与 local Git 边界

- Changed（TASK-0015）: Claude Code 项目入口统一为 `AGENTS.md`，协议不再生成、同步或要求独立 `CLAUDE.md`；其他工具专属兼容入口仍只在目标工具明确需要时保留。Claude Code 的用户级 Skill 安装支持不变。
- Added（TASK-0014）: 每个显式选择的语言 profile 现在生成完整、项目内持久化的 `docs/engineering/profiles/<profile>.md`，文档内记录该 profile 的全部 roots；`AGENTS.md` 一跳按当前路径和实际语言读取，不依赖后续会话再次发现控制 Skill。stamp 的每项 profile 元数据新增 `project_profile`，`source_hash` 改为完整本地化 profile 源 hash；生成文件进入 Git core 与 upgrade/diff 管理。
- Auto（TASK-0014）: legacy schema v1 继续按无 profile 读取；2026.09.7 schema v2 profile stamp 在 `upgrade --apply` 时新增缺失的完整 profile 文件。pristine 文件自动刷新，本地定制与上游同时变化只生成 proposal。既有 `docs/engineering/code-comments.md` 继续保留和升级，绝不因迁移删除或覆盖项目定制。
- Security: stamp 只可列出当前安装明确纳管的文件（含当前已选 profile）或发布侧显式登记的 retired 文件；仅处于合法目录前缀下不构成授权。stamp/profile 路径、role、symlink、hardlink、特殊文件与非 canonical 路径均 fail closed，dirfd 与 portable fallback 的读取、哈希、写入和删除使用同一边界。
- Added: `check` 新增接入持久性 Gate：从安装版本戳 `vault/.agent-init.json` 的受管路径派生协作核心集合（含 stamp 自身），逐路径核对 Git `HEAD`——未提交报 `CORE_STORAGE_UNCOMMITTED` error（合并式 AGENTS.md 的 HEAD 副本还须含受管区块；HEAD stamp 的 `protocol_version` 与核心 files 集合须和当前安装状态相容），被 ignore 规则命中报 `CORE_STORAGE_IGNORED` error 并给出规则来源。已存在但不可读、JSON 非法或 schema 非法的当前 stamp 报 `CORE_STORAGE_INVALID` error；durability 检查兼容 legacy schema v1 与 current v2，拒绝非严格整数或其他版本。Git 验证命令失败报 `CORE_STORAGE_UNVERIFIED` error，非 Git 目标仍报同码 warning。检查只读：读取 HEAD 快照与 `check-ignore --no-index` 规则，不写文件、不改 index、不 commit、不运行 clone；monorepo 子目录按 Git root 相对路径判定。
- Added: `task_storage=local` 项目的边界检查：用固定 sentinel 路径经 `git check-ignore --no-index` 无写入验证未来 TASK（`vault/tasks/TASK-*.md`）、review 台账、`vault/tasks/archive/` 会被忽略，未覆盖报 `LOCAL_BOUNDARY_UNCONFIGURED` warning；`vault/tasks/README.md`、`vault/decisions/`、`vault/details/` 等 durable namespace 被宽泛规则误伤时报 `LOCAL_BOUNDARY_OVERREACH` error（附命中规则与修复方向）。不自动修改任何 `.gitignore`。
- Added: `adopt` 结束输出以场景无关措辞明确"generated ≠ durable"，给出"语义配置 → 用户提交 → 复跑 check → fresh clone 验收"次序，不虚构 dry-run、重复 adopt、非 Git 或部分变化现场的提交状态。TASK-0013 P0/P1 预注册消融正式裁决 Inconclusive（P1 H3=1，未满足冻结 Gate），因此双语 Skill 不加入候选接入完成契约；材料见 `docs/evals/adoption-durability-2026-09/`。
- Breaking: 无工具自动 `git add`/commit/push。未 adopted（无版本戳）的项目不触发核心 Gate，check 行为与 2026.09.7 相同。已 adopted 且核心未提交的项目升级后 `check` 会从 0/0 转为 error——这是真实缺陷暴露，不是回归。
- Agent migration: 升级后首次 `check` 若出现 `CORE_STORAGE_INVALID` / `CORE_STORAGE_UNCOMMITTED` / `CORE_STORAGE_IGNORED` / `CORE_STORAGE_UNVERIFIED`，先修复 stamp 或 Git 验证能力，再由用户提交对应核心文件或收窄 ignore 规则，不得代用户执行 Git 提交；`LOCAL_BOUNDARY_UNCONFIGURED` 按提示补窄规则；`LOCAL_BOUNDARY_OVERREACH` / `LOCAL_BOUNDARY_UNVERIFIED` 修复规则或验证命令后复跑 check 至 0 error，并在 local/生产接入完成时做一次 fresh-clone 复验。

## 2026.09.7 — Profile-aware 代码注释规范与一跳路由

- Added: `adopt --profile PROFILE[=ROOT]` 可重复选择 `go-backend` / `python-backend` 及一个或多个项目相对根目录。选择后只生成一个项目工程文档 `docs/engineering/code-comments.md`，内容为语言无关公共原则加所选语言适配；未选语言不进入文档。`AGENTS.md` 新增源码、公共 API、注释、TODO/FIXME 任务的一跳条件路由，非源码任务无需加载正文，工程规范不写入 Vault。
- Added: `vault/.agent-init.json` schema 2 的 `profiles` 元数据记录 profile id、roots、source hash 和人类可读项目文档路径；旧 schema/stamp 继续按无 profile 读取。升级器把生成的工程规范作为可合并协议载体：本地 pristine 时可刷新，项目定制与上游同时变化时只生成 proposal。
- Breaking: 无。未传 `--profile` 的 adopt 输出集合不新增工程文档；不自动检测语言，不修改业务源码、依赖、lint 或注释率 Gate。已有 `docs/engineering/code-comments.md` 即使 `adopt --force` 也不覆盖；已记录的 profile 集不能通过重复 adopt 静默改写。
- Agent migration: 既有项目只有在 owner 明确选择 profile 与 roots 后才生成规范。可用示例：`trellium.py adopt <target> --profile go-backend=. --profile python-backend=services/model`。若项目已有同名规范，保留本地文件并通过后续 diff/proposal 语义合并，不把正文复制到 Vault。
- Auto: `AGENTS.md` 管理区域与未定制协议文件按既有升级规则刷新；纯旧 stamp 在无文件变化的升级中自动写为 schema 2、`profiles: []`。项目数据文件零替换。

## 2026.09.6 — status unresolved/投影增量形状；控制包模板源更名

- Added: `status` 的 `unresolved` 数组新增两类条目形态。①malformed 短行（少于四列）仅在消息文本中暴露其 task id、不产出 task-scoped finding 时，该 id 以实际 finding 码 `TASK_RUNTIME_INVALID` 物化进 `unresolved`——与 README"无法解析的任务显式列入 unresolved"承诺对齐，`check` 输出零变化；②`vault/` 或 `vault/tasks` 枚举被拒（`SYMLINK_INPUT`）时，输出显式 vault-scope 联合记录 `{"scope": "vault", "path": ..., "reason": "SYMLINK_INPUT"}`（无 `task_id`，不伪造任务 id，不携带 lifecycle/authority），`summary.unresolved` 计数与数组严格一致，消除"从未读取内容却报告 unresolved: 0"的 fail-open 表述。
- Changed: runtime 行分裂出超过四列（如 Next Action 含未转义 `|`）时，该任务的 `runtime_projection` 被抑制（沿用重复行/枚举非法行的既有投影抑制模式），任务保留状态块 lifecycle 分类；此前投影会静默截断且 exit 0 无任何信号。文本渲染对 vault-scope 条目输出 `[vault] path=... reason=...`，与 JSON 同源。
- Changed（TASK-0011 No-Go 停止条件修复，本节标题原 Unreleased 内容一并转正）: 控制包内项目模板源文件更名 `assets/templates/skills/agent-task/SKILL.md` → `AGENT_TASK_SKILL.template`——原文件名可被 Codex 等扫描器全局发现为 `agent-task` Skill（2026-09-15 实测复现）。adopt/upgrade 对目标项目仍渲染/刷新 `skills/agent-task/SKILL.md`，行为与输出不变。
- Auto: 目标项目渲染内容无变化，仅发行包模板源文件名变化（TASK-0011 泄漏修复）；`check` 的发现、严重级与退出码字节级零变化；不新增 schema 版本（JSON 仍为 v1 增量）。

## 2026.09.5 — 只读 status 状态摘要

- Added: `trellium.py status <target>`（`--format json` 可选）：完全只读、确定性的 owner 状态摘要，只编译 `check` 已校验的同一状态层，不新增事实源。输出：Focus（逐个标注 resolved/unresolved）；开放任务按 `draft/active/blocked/ready_for_review` 分类（含 `authority_level`、`task_path` 与可选 `current_slice`/`gates` 原值，runtime 行贡献 `runtime_projection` 的 `objective`/`next_action`）；`accepted`/`superseded` 只进 closed 计数，不进行动清单；无法解析的任务显式列入 `unresolved` 并附阻塞发现码（如 `TASK_RUNTIME_DRIFT`、`TASK_RUNTIME_LOCAL_UNRESOLVED`、`TASK_ID_DUPLICATE`），不声称 lifecycle/authority；runtime 行与状态块冲突（drift）时任务进 unresolved，不裁决哪边为真；重复行或行状态非法的行不产出投影。文本与 JSON v1 从同一份结果渲染，JSON 恒含 `schema_version/target/focus/summary/tasks/findings` 键。退出码与 `check` 一致：error → `2`，仅 warning → `0`，目标/参数错误 → `1`。
- Agent migration: 无。`status` 是新增只读子命令：不新增 schema、依赖、网络或持久状态文件，不推断 owner approval（blocked/pending gate 只显示原值，不是完整 approval inbox），`check` 的发现、严重级与退出码零变化。
- Auto: 无模板变更；`upgrade --apply` 仅刷新版本指针。

## 2026.09.4 — Local TASK 生命周期闭环与 clone-safe 投影

- Added: local 任务进入 `accepted` 前的人工 Durable Knowledge Disposition——任务模板 Memory Updates 新增 `Durable knowledge disposition` 行（`not_applicable | pending | none — <reason> | distilled — <canonical destinations>`）；`pending` 的 local 任务不得进入 `ready_for_review` 或 `accepted`；`none` 需写明理由；`distilled` 只列 canonical 目标文件。tracked 任务默认 `not_applicable`。载体经 W 组消融选定：W1 单行（W1 与 W2 判断等效取更小载体；W0 全对只把增量收益记为 Inconclusive，不构成流程增强 No-Go）。
- Breaking（仅 local 热路径）：local 任务进入 `accepted`/`superseded` 后应删除 `runtime.md` 对应行；checker 对残留的 closed local 行（无论 TASK 文件是否存在）报新 error `TASK_RUNTIME_CLOSED_LOCAL`。tracked 模式关闭后仍可保留 runtime 行，行为不变。
- Added: fresh clone 中 runtime 指向的 missing open local TASK 改报新 warning `TASK_RUNTIME_LOCAL_UNRESOLVED`（同一任务按 row+Focus 去重），文案同时说明可能是正常 fresh clone 或本地误删、恢复动作（取回原任务文件或经 owner 批准重建契约）与 runtime 摘要不授予 Authority。tracked 指针的 `TASK_RUNTIME_MISSING` error 与 policy 缺失时的严格 projection 行为保持不变（C0/C1 characterization 证明仅改协议文档无法消除 local 误报，checker 代码层必要）。
- Agent migration: 不批量回填历史 TASK。升级既有 local 项目时，人工审查 `runtime.md` 中 closed local 行并删除（不删除 local TASK 文件、不自动修改 Git、不自动 untrack）；superseded 转换不受 disposition 阻塞，未处置事项显式转交替代任务或 owner。
- Auto: 未定制模板刷新到 2026.09.4（runtime/tasks README 模板新增 local 语义提示行）；protected data（runtime、handoff、decisions、project、collaboration）仍不自动改写。

## 2026.09.3 — check 状态唯一性与必需文件修复

- Added: `trellium.py check` 新增三类 error 发现：跨任务文件重复 `task_id`（`TASK_ID_DUPLICATE`）、runtime Active Tasks 表重复行（`TASK_RUNTIME_DUPLICATE`）、未关闭任务（draft/active/blocked/ready_for_review）在 runtime 中没有任何 Active Tasks 投影行（`TASK_PROJECTION_MISSING`）。
- Added: 必需文件检查扩展到 `vault/project.md`、`vault/governance.md`、`vault/tasks/README.md`（缺失报 `REQUIRED_FILE_MISSING` warning），与 `10-vault.md` 必备文件清单一致。
- Removed: 计划文档中未实现的 `max_bytes` 未来配置承诺。check 行为不变：预算只有显式配置的阈值会被执行。
- Auto: 无模板变更；`upgrade --apply` 仅刷新版本指针。

## 2026.09.2 — 任务状态块、项目策略块与只读 check

- Added: Level B/C 任务文件标题之后新增 `trellium-task-state` 状态块（schema v1：`schema_version`、`task_id`、`level`、`authority_level`、`lifecycle` 必填；`current_slice`、`gates` 可选），是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner。新建或重新激活任务时添加；历史 TASK 不批量迁移，`check` 对缺失块报 legacy warning、不推断状态。`TASK-*-review.md` 台账与 `tasks/archive/` 不需要状态块。
- Breaking: 任务 lifecycle 统一为 `draft | active | blocked | ready_for_review | accepted | superseded`。`runtime.md` TASK 行改用同一枚举并成为状态块的派生投影；`paused`、`waiting-review` 不再是 TASK 状态，暂停且暂不推进的工作降级为 `parked.md` 条目。
- Breaking: 任务模板删除独立可编辑的 `## Status` 段与 Authority `Level:` 副本；Authority 正文只保留 Allowed、Requires Approval、Forbidden。
- Added: `vault/index.md` 新增 `trellium-policy` 策略块（schema v1）：`task_storage`（`tracked | local`）与可选 `budgets`，是项目预算与 TASK storage 的唯一配置来源；本协议其他位置的预算数字降级为初始化默认值。策略块缺失时 `check` 报 `POLICY_MISSING` warning，不套用隐藏默认值。
- Breaking: `handoff.md` 不再把 Workspace State（分支、HEAD、脏文件）当权威记录；每条交接改为 Objective、Completed、In Progress、Failed Attempts、Blockers、Next Best Action、Files To Read First，实时 Git 事实恢复时现场读取，只可另存一条带观察时间、明确非权威的环境快照。
- Agent migration: `runtime.md`、`handoff.md` 是 protected data，升级不替换；由 Agent 按上述规则以小 diff 方式人工同步，不丢事实。既有项目的 `task_storage` 由 owner 决定（新接入项目默认 `tracked`），工具不自动选择、不修改 `.gitignore`、不自动 untrack。
- Added: `trellium.py check <target>`（`--format json` 可选）：只读确定性校验——状态块/策略块结构与枚举、task_id 与文件名一致、runtime 投影漂移、预算测量与显式阈值、TASK storage 与 Git 实际状态。发现 error 退出 `2`，warning 不改变退出码；全程不写文件、不自动修复。

## 2026.09.1 — 一行安装器与工具修订

- Added: `scripts/install.sh` 一行安装/升级 Skill 包——`curl -fsSL https://raw.githubusercontent.com/zlin101/trellium/develop/scripts/install.sh | sh`。支持 `--lang en|zh`（默认 en）、`--agent codex|claude|all`（默认自动探测 `$CODEX_HOME`/`~/.codex` → codex，`~/.claude` → claude）、`--version`、`--dir`、`--project`（装到当前项目 `.claude/skills`）、`--source`。经 `releases/latest` 重定向解析最新版本（无 API 速率限制）；原地替换，重复执行即升级。
- Auto: 工具变更，无模板变化。`upgrade --apply` 在无文件变更时会把版本戳的 `protocol_version` 刷新到当前版本，避免纯工具版本的版本指针滞后。

## 2026.09.0 — 多任务运行态与挂起区

- Added: `vault/parked.md`（data 角色；`adopt` 与 `upgrade --apply` 会在文件缺失时自动创建，已存在则跳过）。
- Breaking: `vault/runtime.md` 模板 `Active Task` 小节改为 `Focus` 行 + `Active Tasks` 指针表（每行一个并行任务：任务编号、一句话目标、状态、下一步）。
- Breaking: `vault/handoff.md` 模板改为条目式，每条交接以任务编号命名（无任务编号时用 SESSION）。
- Agent migration: 已有定制的 `runtime.md` 是项目数据，永不模板替换——把现有 Active Task 内容改写为指针表一行，`Focus` 指向该任务；`Current Progress` 条目逐条保留或按压缩规则分流；不丢任何事实。向用户提案后执行。
- Agent migration: 已有定制的 `handoff.md` 同理——把现有快照内容改写为一条以任务编号命名的交接条目；无任务编号的用 SESSION。
- Added: review 台账——`vault/tasks/TASK-xxxx-review.md`（运行时创建，不由 adopt 下发）；80 号模块新增 Review Ledger 执行模式；`tasks/README.md` 模板含台账格式。
- Breaking: runtime 的 Recent Changes 上限 10 条，超出走压缩分流；热文件更新纪律成文（每条一行、单行替换、不重写整段）。
- Added: `trellium.py --fetch`——从 GitHub 拉取最新 tag release 并以该版本的脚本与模板执行；协议内容更新无需重装 Skill 包。各命令支持 `--templates <dir>` 覆盖模板目录。
- Auto: `vault/index.md`、`vault/tasks/README.md`（如未变）、`skills/agent-task/SKILL.md`（如未变）按升级分级格自动刷新；定制过的 `index.md` 走提案合并 parked 路由条目。

## 2026.08.0 — 初始版本化发布

- 确立热文件预算线与五阶段压缩（vault compaction）为基线能力。
- Added: 升级机制本身——`trellium.py baseline|diff|upgrade` 与 `vault/.agent-init.json` 版本戳；升级器对项目数据只读，协议文件本地修改永不静默丢弃。
- Agent migration: 本版本之前接入、尚无版本戳的项目，先运行 `python3 trellium.py baseline <target>` 补记版本戳（unversioned 信任级，首次升级全部走提案）。
- Auto: 此后每次模板变更由 `diff` 报告；`upgrade --apply` 只替换未被项目修改过的协议文件，冲突生成提案到 `vault/.upgrade/<version>/`。
