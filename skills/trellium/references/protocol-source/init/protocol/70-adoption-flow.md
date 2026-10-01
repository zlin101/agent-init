# 70 - 既有项目接入流程

## 定位

接入流程用于已经存在的项目。

目标是在不改变既有工程代码、依赖、业务结构和运行逻辑的前提下，引入 Agent-Native 的记忆管理、任务治理和交接机制。

它不是新项目初始化，也不是工程迁移。

一句话定义：

> 接入模式只安装或更新 Agent 协作层，不改业务工程层。

## 适用场景

- 已有项目希望引入 `vault/` 项目记忆系统。
- 已有项目希望引入由 Claude Code 等兼容工具共享的 `AGENTS.md` 入口规则。
- 已有项目希望引入任务契约、授权等级、验收门和 handoff 机制。
- 已有项目希望规范多 Agent 接力，但不调整代码结构。

## 允许修改

默认只允许创建或更新 Agent 协作层文件：

- `AGENTS.md`
- `CODEX.md`、`GEMINI.md` 等仍有明确需要的工具兼容入口，按项目需要创建；Claude Code 直接使用 `AGENTS.md`
- `vault/`
- `vault/index.md`
- `vault/project.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions.md`
- `vault/handoff.md`
- `vault/project-id`，仅由 local/private 接入的 bundled 身份 helper 创建或校验（Local tracked、Private ignored；升级永不重建或覆盖；tracked 不创建）
- `vault/tasks/README.md`
- `vault/tasks/.gitkeep`
- `vault/details/*`，仅在已有项目确实需要时创建
- `skills/`
- `skills/trellium-work/SKILL.md`
- `docs/engineering/profiles/<profile>.md`，仅在 owner 显式选择语言 profile 时生成；每个已选 profile 一份完整工程规范
- `docs/engineering/code-comments.md`，项目的 Comment/API Documentation Policy（注释/API 文档表达规范的唯一 owner）；它与完整 profile 都是项目工程文档，不是 Vault 数据

可选修改：

- `README.md` 中添加极短 Agent 协作说明，但必须先说明，并尽量避免打扰原 README 结构。

## 禁止修改

除非用户明确授权，接入模式禁止修改：

- 业务源码目录，例如 `app/`、`src/`、`lib/`、`packages/`
- 测试目录，例如 `tests/`、`spec/`、`__tests__/`
- 依赖文件，例如 `pyproject.toml`、`package.json`、`go.mod`、`Cargo.toml`
- 锁文件，例如 `uv.lock`、`package-lock.json`、`pnpm-lock.yaml`、`Cargo.lock`
- 构建、部署或 CI 配置，例如 `Dockerfile`、`.github/workflows/*`
- 数据库迁移、配置文件或环境文件
- 既有业务文档的大段内容
- 任何真实密钥、Token、密码或凭据

如果接入需要触碰上述文件，必须升级为用户确认事项。

## 接入前扫描

Agent 执行接入前，应只做只读扫描：

1. 查看根目录文件。
2. 查找既有 Agent 入口文件：`AGENTS.md`、`CODEX.md`、`GEMINI.md`、`.cursor/rules`。
3. 查找既有项目文档：`README.md`、`docs/`、`CONTRIBUTING.md`。
4. 查找既有记忆或任务目录：`vault/`、`memory/`、`docs/adr/`、`decisions/`。
5. 识别项目类型和技术栈，但不改依赖或代码。
6. 如需语言工程规范，明确 profile 与适用根目录；多语言或同语言多根目录使用重复选择，不自动猜测。
7. 检查工作区是否已有未说明的变更。
8. 在任何目标写入前通过下方「存储模式选择门」；未明确模式时等待回答，已有明确选择或既有有效 policy 则复用。

扫描后，Agent 应给出接入计划，列出将创建或修改的协作层文件。

## 存储模式选择门

安装 Skill 包与接入具体项目是两个阶段；storage 只写入目标项目的 `vault/index.md` policy，不设全局模式。只安装包且目标项目未知时，模式问题留到首次项目接入。

首次项目接入没有 owner 对本项目的明确选择时，问一个问题：“这个项目采用 Private、Local 还是 Tracked？”并说明 Git 可见性：Private 的全部目标 managed material 留在本机；Local 的协作核心进 Git、TASK/review/archive 留本机；Tracked 的协作核心与完整任务流水进 Git。Private/Local 可按 History 契约在本机保全 terminal TASK/review，默认 root `~/.trellium/history`，不自动备份当前 Vault或跨机器同步。

推荐 Local 只作为建议；预选、未回答或等待超时不算选择。等待期间仅可继续只读扫描：不运行 adopt、不创建接入 TASK 契约、不写任何目标项目文件。当前对话或既有授权已明确本项目模式时，接入摘要说明并直接复用，不重复询问。

已接入项目先读取有效 policy，重复接入/升级保留模式。policy 缺失、无效或与当前请求冲突时，先澄清再写入；不能把既有项目当作全新项目套默认值，不能自动迁移或 untrack。此门是 Skill/Agent 接入契约，不新增 CLI 参数，裸调用低层 adopt 不提供交互式选择保证。

## 冲突处理

### 已存在 AGENTS.md

不要直接覆盖。

处理方式：

1. 读取原文件。
2. 保留项目已有规则。
3. 在不削弱原规则的前提下，加入 vault 和 governance 读取规则。
4. 如规则冲突，先指出冲突并请求确认。

### 已存在 CODEX.md / GEMINI.md 等工具兼容入口

保持与 `AGENTS.md` 语义一致。

工具专属说明可以保留，但不得覆盖通用治理规则。

### 已存在 vault/

不要覆盖。

处理方式：

1. 读取现有结构。
2. 缺什么补什么。
3. 已有文件先合并，不直接替换。
4. 对语义冲突的内容请求确认。

### 已存在 docs/adr 或 decisions

不要迁移历史记录。

在 `vault/decisions.md` 中添加指针，说明长期决策还可能存在于原位置。

### 已存在 README.md

默认不修改。

如需要添加 Agent 协作说明，只添加短段落，并避免重写原 README。

## 接入步骤

1. 读取 `init/INIT.md`。
2. 读取 `init/protocol/README.md`。
3. 读取 `init/protocol/10-vault.md`。
4. 读取 `init/protocol/20-governance.md`。
5. 读取 `init/protocol/30-agent-entry.md`。
6. 读取 `init/protocol/40-skills.md`。
7. 执行接入前扫描。
8. 输出接入计划，说明将创建或修改哪些协作层文件。
9. 合并或创建 Agent 入口文件。
10. 合并或创建 `vault/`；local 模式由 Agent 生成窄范围 `vault/tasks/.gitignore`，只忽略 `TASK-*.md`、`*-review.md` 与 `archive/`，不修改项目根 `.gitignore`。local 模式在 policy 与窄范围 ignore 就位后调用 bundled 身份 helper 完成首次身份绑定：fresh 接入在接入计划中说明身份创建，存量 local 首次启用须取得 owner 确认绑定；helper 将 `vault/project-id` 以 `data` role 登记进版本戳，绑定丢失或登记失败按 helper 报告恢复/重试；随后运行 check，0 error 才算接入完成。Private 完成下方 policy/exclude 后也调用该 helper，保持身份 ignored；tracked 不触发身份创建。
11. 合并或创建 `skills/`。
12. 在 `vault/project.md` 记录“这是既有项目接入，不是新项目初始化”。
13. 在 `vault/runtime.md` 记录接入状态、风险和下一步。
14. 在 `vault/decisions.md` 记录接入决策。
15. 仅当发生真实中断且存在非可推导 transient delta 时，更新 `vault/handoff.md`（未完成事项本身不触发 handoff；普通接入与规划不产生 handoff）。
16. 运行只读或文档级检查；不要运行会改变工程状态的命令，除非用户授权。

## 接入验收

接入完成必须满足：

- 未修改业务源码。
- 未修改依赖和锁文件。
- 未修改测试、构建、部署或 CI 配置。
- Agent 入口文件会路由到 `vault/index.md` 和 `vault/runtime.md`，并在 Level B 或 Level C、判定模糊或涉及治理规则时路由到 `vault/governance.md`。
- `vault/` 必备文件存在。
- policy 中的 TASK storage 与 owner 选择一致；local 边界只覆盖 TASK/review/archive，tracked 不忽略这些路径。
- `vault/governance.md` 定义任务等级、授权等级、任务契约、验收门和接力规则。
- `skills/trellium-work/SKILL.md` 存在。
- `vault/runtime.md` 明确记录接入完成状态。
- `vault/decisions.md` 记录接入模式决策。
- 所有冲突和未完成事项已记录或请求确认。

## 协作层升级

接入之后，协议源仍会演进。升级的目标是：协议文件跟进新版，项目数据零损失，项目发展路线不中断。

重复 adopt 和 upgrade 必须保持既有 `storage_mode`。显式选择与既有 policy 冲突时，在写入前失败；mode 迁移属于 owner 单独评审动作，工具不自动迁移、不自动 untrack。

升级器是 `trellium.py`，有两种运行位置：仓库 checkout 的 `scripts/trellium.py`（协议开发维护用），或已安装 Skill 包内的 `assets/trellium.py`（最终用户的常规路径，由 `sync-skills.py` 自动分发并与 `scripts/trellium.py` 保持一致）。下文命令中的 `trellium.py` 指两者任一。

adopt/diff/upgrade 可加 `--fetch`：从 GitHub 拉取最新 tag release（缓存于 `~/.cache/trellium/`），以该版本的脚本与模板执行——协议内容更新因此不需要重装 Skill 包；目标版本低于项目已装版本时拒绝执行。`--templates <dir>` 可覆盖模板目录（版本信息仍随运行脚本）。

### Profile 工程规范

本节是 Profile 工程规范的唯一 canonical 定义：产物集合、文件角色、roots、已有文件保护与 proposal、AGENTS 路由语义以本节为准；其他文档只保留摘要并指向本节，不重复完整规则。

`adopt --profile PROFILE[=ROOT]` 可重复使用，例如：

```bash
python3 trellium.py adopt <target> \
  --profile go-backend=services/api \
  --profile python-backend=services/model
```

工具为每个已选 profile 生成完整的 `docs/engineering/profiles/<profile>.md`，把该 profile 的全部 roots 写入文件，并让 `AGENTS.md` 一跳按当前路径与实际语言读取；多语言不共享正文，也不加载未匹配 profile。`docs/engineering/code-comments.md` 生成/保留为项目的 Comment/API Documentation Policy（注释/API 文档表达规范的唯一 owner）；2026.09.7 项目定制继续保留在其中。表达规则重叠处以 Comment Policy 为准，其余工程事项由完整 profile 约束。Profile 必须显式选择，不自动猜测；未选 profile 不生成任何工程文档。选择、roots 与完整源 hash 记录在 `.agent-init.json`，stamp 分别记录完整 profile（`project_profile`）与兼容载体（`project_rules`）两个文件角色的项目路径，便于确定性升级；人类可读规范仍以项目文档为准。已有规范（包括 `adopt --force`）不静默覆盖，后续上游与本地同时变化时走 proposal。改变既有 profile 集属于显式评审迁移，不由重复 adopt 偷偷改写。

### Private 存储模式

`storage_mode=private`（schema v2 policy）让目标项目的全部 Trellium managed material 不进入 Git：untracked、由 Git root `.git/info/exclude` 中带 target identity 的 canonical `# trellium-private:start/end` block 精确忽略，不进入 Git index、HEAD 或远端；terminal TASK/review 可另存本机 History Store，当前 Vault 不因此获得备份。Private 是显式选择，不自动迁移既有 tracked/local 项目。

Private 接入的 Agent-native 顺序：

1. adopt 之前调用 bundled 脚本的只读探针 `private_preflight(target, profiles)`：任一候选 managed path（AGENTS、Vault、trellium-work Skill、stamp、Comment Policy、所选完整 Profile）已 tracked 或在 HEAD 中即拒绝；Git 查询失败 fail-closed；探针零写入。
2. `adopt` 正常生成文件后，Agent 将 policy 写为 schema v2 `storage_mode=private`，并在 `.git/info/exclude` 维护 canonical private block（anchored patterns 精确覆盖全部 managed paths，不允许 overreach 或后置 negation）。
3. policy/exclude 就位后调用 bundled ensure_project_identity helper（调用方法见分发 Skill），复用/登记 ignored 的 vault/project-id，只有显式首次绑定授权才能创建；helper 在写入前验证 stamp、Git 证据与 private 边界，登记 baseline 不符或已绑定身份丢失时拒绝替换。
4. 运行 check；private storage finding 为零才算接入完成。Private TASK 使用 local lifecycle、knowledge disposition 和 terminal History 保全（见 10-vault.md）。fresh clone 不包含原协作层；找回历史须保留/恢复原 UUID，重新接入时先 get 核对已知历史、恢复该 UUID 文件、调用 helper 复用登记，不能自动创建新身份冒充旧历史；不恢复旧 Authority。

升级语义：upgrade/diff/proposal 不执行 Git 写入；untracked managed 文件不视为 dirty；Private 完成提示是保持 untracked/ignored 并重跑 check，不得提示 commit。Checker 反向 privacy Gate：`PRIVATE_STORAGE_TRACKED`（含 `git add -f`）、`PRIVATE_STORAGE_UNCONFIGURED`（block 缺失/畸形/重复，或按实际 `git check-ignore` 结果未被 ignore）、`PRIVATE_STORAGE_OVERREACH`、`PRIVATE_STORAGE_UNVERIFIED`（Git 查询失败、缺 stamp、managed 唯一副本缺失或非普通文件）全部 error fail-closed；非 Git 目标为 warning。

### 文件两分法

升级器把协作层文件分成两类，写入权限不同：

| 类 | 文件 | 升级权限 |
| --- | --- | --- |
| 项目数据 | `runtime.md`、`handoff.md`、`decisions.md`、`decisions/`、`tasks/*`、`project.md`、`collaboration.md`、`details/*` | 只读。写入范围是硬编码白名单，数据文件不在其中，不依赖 Agent 自觉 |
| 协议文件 | `governance.md`、`index.md`、`tasks/README.md`、`skills/trellium-work/`、`AGENTS.md`、显式选择后生成的 `docs/engineering/profiles/*.md` 与兼容 `code-comments.md` | 可写。本地未改的跟进上游；本地改过且上游也改过的出冲突提案 |

`vault/.agent-init.json` 是升级器的版本戳：记录每个文件上次安装时的内容 hash，用于区分"项目自己改的"和"上游旧模板"。`AGENTS.md` 有两种形态：从模板整文件创建的按整文件对比；追加到用户已有文件的，只管理 marker 标记区域。

stamp 不是文件权限来源：可读写或删除的路径必须属于当前协议的精确 managed-file 集合；profile 文件只包含当前项目显式选择的 profile，退役文件必须由发布侧逐项登记。合法目录前缀、stamp 自报 role 或存在于项目内都不能扩大权限；所有路径与文件类型校验在 dirfd 和 portable fallback 两条路径上都 fail closed。

### 铁律

1. 数据文件永不被模板替换。数据文件需要换格式时，按 `init/MIGRATIONS.md` 的迁移手册做内容搬运：同一批事实、新排版，Agent 提案、用户确认，不允许"判断不重要然后丢弃"。
2. 协议文件的本地修改永不静默丢弃：本地未改 → 跟进上游；仅本地改 → 保留；双方都改 → 冲突提案，由 Agent 语义合并、用户确认。语义合并后的文件标记为 observed，此后上游再变也只出提案，不自动替换。
3. 先报告后执行：`diff` 只读；`upgrade` 默认 dry-run，`--apply` 只执行安全子集。
4. 升级逐文件可选：`--only` / `--skip` 允许部分采纳；跳过的文件下轮再补。
5. 目标为 git 仓库时，待触碰文件必须无未提交变更（`--allow-dirty` 显式覆盖）；非 git 目标先备份到 `.agent-init-backup/`。升级产出独立提交，可随时 `git revert`。

### 升级轮次

1. `python3 trellium.py diff <target>`：只读报告（apply / conflict / add / keep / protected）与待执行迁移手册。
2. `python3 trellium.py upgrade <target> --apply`：执行安全子集（pristine 替换、新增、删除）；冲突生成提案到 `vault/.upgrade/<version>/`，含上游新版本与 upstream→local 差异。
3. Agent 按提案合并 → 用户逐个确认。
4. `python3 trellium.py upgrade <target> --complete`：登记合并结果，收尾版本。中断安全：pending 状态持久在版本戳中，重跑 `diff` 可见卡点。

### 存量项目接入

版本戳出现之前接入的项目，先运行 `python3 trellium.py baseline <target>` 补记版本戳（unversioned 信任级）：以当前本地内容为基线，此后上游变更一律出提案、不自动替换；首轮升级完成后恢复完整分级。

### 发布侧约束

每次修改协议模板：若新增或删除下发的模板文件，同步更新 `scripts/trellium.py` 的 `FILE_ROLES`；在 `init/MIGRATIONS.md` 追加条目并按需更新 `init/VERSION`。发布供 `--fetch` 使用的版本时打 tag（与 `init/VERSION` 一致）：`git tag <版本号> && git push origin <版本号>`。

## 接入模式的授权

接入模式默认属于 Authority 2。

如果需要修改 README 的短说明，仍可视为 Authority 2，但必须提前说明。

如果需要修改源码、依赖、测试、构建、部署或 CI，必须升级为 Authority 3，并取得用户确认。

## 接入输出建议

Agent 完成接入后，应向用户报告：

- 创建或修改了哪些协作层文件；
- 明确没有触碰哪些工程代码或配置；
- 发现了哪些既有规则或冲突；
- 后续 Agent 应从哪些文件开始读取；
- 是否存在需要用户确认的剩余事项。
