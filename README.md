# Trellium

[English](README.en.md) | 简体中文

Trellium 是一套可迁移的 Agent 协作协议：为项目安装并持续升级 Agent 协作层。

它的目标不是生成某个固定技术栈的应用模板，而是给任何项目接入一层稳定的 Agent 协作能力：入口规则、项目记忆、任务治理、验收门、交接机制、可复用工作流和协作画像。

## 这个项目解决什么

长期使用 AI Agent 开发时，常见问题不是“Agent 不会写代码”，而是：

- 新会话不知道项目当前状态；
- Agent 没有清晰授权边界；
- 任务做到一半无法交接；
- 测试通过但验收没有关闭；
- 重要决策散落在聊天记录里；
- 多 Agent 或多工具切换时上下文断裂；
- 每个项目都要重新口头约定一套协作规则。

Trellium 把这些约定收敛为一套项目级协作协议，让 Agent 进入项目后知道：

- 先读什么上下文；
- 如何判断任务等级和授权等级；
- 哪些文件承载运行态、决策和交接；
- 什么情况下必须创建任务文件；
- 怎样验证任务完成；
- 哪些协作偏好可以沉淀，哪些不能覆盖硬规则。

## 核心产物

本仓库真正可迁移的核心分为两类：

```text
init/
skills/
```

`init/` 是协议源目录。它用于维护 Trellium 的完整设计、初始化与升级流程。

`skills/` 是可直接安装的自包含 Skill 包。它从 `init/` 协议源收敛而来，内含主工作流、协议精华 reference、自动同步的权威协议快照和可复制模板，不依赖本仓库本地路径。

仓库根目录中的 `AGENTS.md`、`vault/`、`app/`、`tests/` 等，是当前沙盒根据协议生成出来的验证产物，不是迁移源。

如果只想安装一个自包含 Skill，而不是迁移完整协议源，可以使用：

```text
skills/trellium/
skills/trellium-zh/
```

`trellium` 是英文版，`trellium-zh` 是中文版。

## 目录结构

```text
init/
  INIT.md                         # 初始化入口清单
  VERSION                         # 协议版本号（CalVer）
  MIGRATIONS.md                   # 升级迁移手册（数据保护条目）
  protocol/
    README.md                     # 协议模块说明
    00-overview.md                # 总体定位和分层
    10-vault.md                   # 项目记忆系统
    15-vault-compaction.md        # 记忆压缩与预算线
    20-governance.md              # 任务治理、授权和验收
    30-agent-entry.md             # Agent 入口文件规则
    40-skills.md                  # 可复用工作流
    50-engineering-constraints.md # 工程约束
    60-initialization-flow.md     # 新项目初始化流程
    70-adoption-flow.md           # 既有项目接入流程
    80-execution-patterns.md      # Agentic 执行模式
    90-collaboration-profile.md   # 可演化协作画像
    profiles/
      go-backend.md               # Go 后端 profile
      python-backend.md           # Python 后端最小 profile
skills/
  trellium/               # 自包含开源 Skill 包
  trellium-zh/            # 自包含开源 Skill 包中文版
scripts/
  trellium.py                      # 安装/升级协作层脚本（sync 自动分发进 Skill 包）
  sync-skills.py                   # 将 init/ 同步到 Skill 分发包
.github/workflows/
  skill-sync.yml                   # 检查协议源和 Skill 快照是否一致
```

## 使用方式

### 新项目初始化

在目标项目中让 Agent 读取：

```text
init/INIT.md
init/protocol/README.md
init/protocol/60-initialization-flow.md
```

如果项目类型已明确，再读取对应 profile，例如：

```text
init/protocol/profiles/python-backend.md
init/protocol/profiles/go-backend.md
```

Agent 应根据协议在目标项目中生成自己的：

- Agent 入口文件，例如 `AGENTS.md`；
- `vault/` 项目记忆系统；
- `vault/governance.md` 协作治理规则；
- `vault/tasks/` 任务契约规则；
- `skills/` 可复用工作流；
- 必要时的项目源码、测试和依赖文件。

### 既有项目接入

如果目标项目已经存在，只想接入 Agent 协作层，让 Agent 读取：

```text
init/INIT.md
init/protocol/README.md
init/protocol/70-adoption-flow.md
```

接入模式默认只创建或更新 Agent 协作层：

- Agent 入口文件；
- `vault/`；
- `skills/`；
- 可选的极短 README 协作说明。

除非用户明确授权，否则不要修改业务源码、依赖、测试、构建、部署或 CI 配置。

### 使用开源 Skill 包

如果你的 Agent 环境支持安装 Skills，可以将以下目录作为 Skill 包安装或复制：

```text
skills/trellium/
skills/trellium-zh/
```

使用该 Skill 时，Agent 会按包内 reference 和 templates 在目标项目中生成或合并：

- Agent 入口文件；
- `vault/` 项目记忆；
- 任务契约治理；
- handoff 和 collaboration profile；
- `skills/agent-task/SKILL.md` starter workflow。

该 Skill 适合跨项目复用；完整 `init/protocol/` 更适合继续设计和维护协议本身。每个 Skill 的 `references/protocol-source/` 是由 `init/` 自动生成的权威快照，不要直接修改。

重装 Skill 即获得新版模板、协议快照与内置升级脚本。对已接入项目，让 Agent 按 SKILL.md 的升级流程执行：`diff`（只读报告）→ `upgrade --apply`（安全子集 + 冲突提案）→ Agent 语义合并 + 用户确认 → `upgrade --complete`。项目数据（runtime、handoff、decisions、tasks）对脚本只读，永不被模板替换。

### 一行安装（任意 Agent）

```bash
curl -fsSL https://raw.githubusercontent.com/zlin101/trellium/develop/scripts/install.sh | sh -s -- --version 2026.09.9
```

安装英文 Skill 包到自动探测的 agent 目录（`$CODEX_HOME`/`~/.codex` → Codex；`~/.claude` → Claude Code）。常用参数：

```bash
... | sh -s -- --lang zh              # 中文包（默认 en）
... | sh -s -- --agent all            # 同时装 Codex 与 Claude Code
                                     # 不指定时自动探测：$CODEX_HOME/~/.codex → codex，~/.claude → claude
... | sh -s -- --project              # 装到当前项目 ./.claude/skills/
... | sh -s -- --version 2026.09.9    # tag-only 发布必须显式指定版本
... | sh -s -- --dir <路径>           # 任意目标目录
```

重复执行即原地升级（替换整个包目录）。脚本按 `--version` 从 GitHub tag 下载 tarball 并拷贝一个目录，可先 `curl -fsSL <url> | less` 审计再执行。不传版本的安装会直接失败（latest-release 解析已按 TASK-0024 移除）：网络安装必须显式 `--version <tag>`，本地安装用 `--source <dir>` 无需版本。

### 使用 Codex 安装 Skill

推荐使用 Codex 内置的 `skill-installer`，从 GitHub 仓库直接安装本 Skill。用户不需要 clone 本仓库，只需要本机已安装 Codex 且能访问 GitHub。

中文版：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/trellium \
  --path skills/trellium-zh
```

英文版：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/trellium \
  --path skills/trellium
```

安装后重启 Codex，让新 Skill 生效。

已安装的 Skill 不会随 GitHub 仓库自动升级。**协议模板与升级器的更新不需要重装 Skill**：升级命令加 `--fetch` 即从仓库拉取最新 tag release 执行（缓存于 `~/.cache/trellium/`，降级会被拒绝）。仅当 Skill 工作流（`SKILL.md`）或脚本自身变化时才需要移除旧的本地 Skill 目录重装；Codex installer 默认拒绝覆盖已存在目录。重新安装前应确认本地 Skill 目录没有需要保留的自定义修改。

如果仓库尚未推送到 GitHub，先推送包含 `skills/trellium-zh/` 或 `skills/trellium/` 的提交，再让 Codex 安装。

### 使用脚本接入项目

`trellium.py` 是安装/升级的确定性执行器，有两种运行位置：Skill 包内的 `assets/trellium.py`（最终用户常规路径，随包分发），或本仓库 checkout 的 `scripts/trellium.py`（协议开发维护用）。两者由 `sync-skills.py` 保持一致，下文命令以仓库路径示例。

对既有项目接入 Agent 协作层：

```bash
python3 scripts/trellium.py adopt /path/to/project
```

首次使用 Skill 时，Agent 会询问 TASK storage，并推荐/默认 `local`：只有 `vault/tasks/TASK-*.md`、review 台账和 archive 留在本地，协作核心仍进入 Git；需要共享完整任务流水时选择 `tracked`。这是 Agent 工作流，不新增 CLI 参数：Agent 在 adopt 后把选择写入 policy，并在 local 模式补充窄范围 `vault/tasks/.gitignore`。重复接入与升级保持已有选择，storage 迁移不会自动执行。

`local` 与 `private` 的 terminal TASK/review 都可按 Skill 流程成组保全到本机 `~/.trellium/history`，失败保留来源、读回校验后才算完成。Local 的 `vault/project-id` 进入 Git，Private 的身份文件随 Vault ignored；Private 写入前必须通过 privacy 边界校验，已登记身份丢失或改变时要求恢复。删 clone 后按保留的原 UUID、artifact id、digest 找回历史；新 private 接入显式恢复原 UUID，不从路径/remote 猜身份。换机器需迁移 Store 与 UUID，没有自动同步，也不备份当前 Vault。完整调用和恢复流程见 [中文 Skill](skills/trellium-zh/SKILL.md)。默认仍 Local，不自动迁移既有项目。

项目语言已明确时，用可重复的 `--profile PROFILE[=ROOT]` 显式声明作用域；同语言可有多个 root，多语言各自使用独立项目文档：

```bash
python3 scripts/trellium.py adopt /path/to/project \
  --profile go-backend=services/api \
  --profile python-backend=services/model
```

这会为每个已选 profile 生成完整的 `docs/engineering/profiles/<profile>.md`（含 roots），并在 `AGENTS.md` 添加按当前路径和实际语言触发的一跳路由；未选 profile 不生成，后续会话不依赖再次发现 Trellium Skill。`docs/engineering/code-comments.md` 作为项目的 Comment/API Documentation Policy 继续保留：注释/API 文档表达规范由它唯一拥有，其余工程事项由完整 profile 约束。工程规范正文不进入 Vault；roots、已有文件保护与升级 proposal 等完整规则见 `init/protocol/70-adoption-flow.md`「Profile 工程规范」。

`adopt` 默认只新增缺失的 Agent 协作文件：

- `AGENTS.md`
- `vault/`
- `vault/tasks/README.md`
- `skills/agent-task/SKILL.md`

如果目标项目已经有 `AGENTS.md`，脚本会追加一个带标记的 Trellium 小节，而不是覆盖原文件。已有的 `vault/*` 和 `skills/*` 文件默认跳过；需要替换时显式传入 `--force`。

任何写入发生前，脚本会预检全部输出路径。如果预检发现输出文件或目标目录内的任一父路径是符号链接、输出文件具有多个硬链接，或者解析后的路径越出目标目录，整次接入会在零写入状态下失败。文件内容通过同目录临时文件原子替换；在支持 `dir_fd` 和 `O_NOFOLLOW` 的平台上，实际写入还会从文件系统根开始逐级锚定目录句柄，阻止预检后的换链绕过。如果运行期间检测到文件系统竞态或发生 I/O 故障，脚本会停止并明确提示目标可能已有部分变更。

接入后，在目标项目里让 Agent 读取：

```text
AGENTS.md
vault/index.md
vault/runtime.md
vault/governance.md
```

### 升级已接入项目

协议源演进后，已接入的项目可以安全跟进，且不影响项目自身的发展路线（Skill 包用户将 `scripts/trellium.py` 替换为 `<skill 目录>/assets/trellium.py`；adopt/diff/upgrade 可加 `--fetch` 直接拉取最新 tag release，无需等待 Skill 重装）：

```bash
python3 scripts/trellium.py diff /path/to/project              # 只读报告
python3 scripts/trellium.py upgrade /path/to/project --apply   # 执行安全子集
python3 scripts/trellium.py upgrade /path/to/project --complete  # 提案解决后收尾
```

升级把协作层文件分为两类：**项目数据**（runtime、handoff、decisions、tasks、project、collaboration 等）对升级器只读，永不被模板替换；**协议文件**（governance、index、tasks/README、skills/agent-task、AGENTS.md 管理区域，以及显式选择后生成的工程规范）可刷新，但本地修改永不静默丢弃——双方都改过时生成提案到 `vault/.upgrade/<version>/`，由 Agent 合并、用户确认。升级逐文件可选（`--only` / `--skip`），产出独立提交可随时 `git revert`。

`adopt` 会在 `vault/.agent-init.json` 记录版本戳（各文件安装时的内容 hash）。版本戳出现之前的存量项目先运行 `baseline <target>` 补记。数据文件的格式迁移由 `init/MIGRATIONS.md` 迁移手册逐条定义：只做内容搬运，不丢事实。

### 校验项目状态（check）

```bash
python3 scripts/trellium.py check /path/to/project                # 文本报告
python3 scripts/trellium.py check /path/to/project --format json  # 稳定 JSON
```

`check` 是完全只读、确定性的校验命令，面向 2026.09.2 引入的最小状态层：

- `trellium-task-state` 状态块：Level B/C 任务文件顶部的严格 JSON 块，是 lifecycle、授权等级、当前 slice 与 Gate 结果的唯一 owner；
- `trellium-policy` 策略块：`vault/index.md` 中的项目策略，唯一配置预算与 `storage_mode`（`tracked | local | private`）；
- 预算测量：热文件行数、UTF-8 字节、最大单行、条目数始终报告；只有策略块显式配置的阈值会触发 `BUDGET_EXCEEDED` warning（仓库健康信号，不阻塞验收）；
- TASK storage：按 `storage_mode` 对比 Git 实际状态（tracked/local/private）；tracked 模式还从 Git index 只读识别已索引 TASK 在 working tree 中被删除；private 模式要求全部 managed material untracked 且被 trellium-private block 精确忽略，TASK 使用 local lifecycle 语义；
- 接入持久性（2026.09.8）：从安装版本戳派生协作核心集合（含 stamp 自身）并逐路径核对 Git `HEAD`——当前 stamp 损坏报 `CORE_STORAGE_INVALID` error，未提交或 HEAD stamp 与当前协议版本/核心集合不相容报 `CORE_STORAGE_UNCOMMITTED` error，被 ignore 规则误伤报 `CORE_STORAGE_IGNORED` error（附命中规则）；Git 验证失败报 `CORE_STORAGE_UNVERIFIED` error，非 Git 目标报同码 warning。private 模式跳过该正向 Gate，改用反向 privacy Gate：managed material 必须 untracked 且被 trellium-private block 精确忽略，tracked/staged 即 `PRIVATE_STORAGE_TRACKED` error。fresh clone 是 local/生产接入的一次性验收动作，不进入日常 check；
- local 边界（2026.09.8；2026.09.9 默认接入）：`task_storage=local` 时用无写入 sentinel 验证未来 TASK/review/archive 会被忽略（未覆盖报 `LOCAL_BOUNDARY_UNCONFIGURED` warning），并验证 `vault/tasks/README.md`、`vault/decisions/`、`vault/details/` 等 durable namespace 不被宽泛规则误伤（命中报 `LOCAL_BOUNDARY_OVERREACH` error，附规则与修复方向）；Git 边界命令失败报 `LOCAL_BOUNDARY_UNVERIFIED` error。新 local 接入生成窄范围 `vault/tasks/.gitignore`，但 checker 本身仍只读，既有项目也不会被自动迁移或修改根 `.gitignore`。

退出码：发现 error 退出 `2`；只有 warning 退出 `0`，但 summary 必须显示 warning，不会显示无条件 PASS；目标无效等操作错误退出 `1`。`check` 不会自动修复任何文件、不写入目标项目、不访问网络、不执行文档中出现的命令。

对旧项目是 fail-closed 的：没有状态块的历史 TASK 报 legacy warning，不推断状态；没有策略块时不套用隐藏默认值。状态块不授予批准——Allowed、Requires Approval、Forbidden 与验收始终由任务正文与用户指令决定。

采用 local lifecycle 语义（`storage_mode=local` 或 `private`）的任务进入 `accepted` 前还需人工完成 Memory Updates 中的 Durable knowledge disposition（`none — <理由>` 或 `distilled — <canonical 目标文件>`；未填写视为 `pending` 并阻塞 `accepted`）；错误契约走 `superseded` 立即废止，不受该 gate 阻塞。

### 查看所有者状态摘要（status，2026.09.5）

```bash
python3 scripts/trellium.py status /path/to/project                # 文本摘要
python3 scripts/trellium.py status /path/to/project --format json  # 稳定 JSON v1
```

`status` 是完全只读、确定性的 owner 状态摘要命令（2026.09.5 引入）。它直接扫描 `check` 校验的 canonical TASK 状态块，不新增事实源：

- Focus 行逐个标注 resolved/unresolved，但只用于导航；缺失 Focus 不使 TASK lifecycle unresolved；
- 开放任务按 `draft / active / blocked / ready_for_review` 分类，每项给出 `authority_level`、任务文件路径与可选的 `current_slice`/`gates` 原值；
- `accepted`/`superseded` 只进 closed 计数，不进入行动清单；
- 无法解析的 canonical TASK state 显式列入 `unresolved`，绝不推断 lifecycle 或 authority；
- 退出码与 `check` 一致（error → `2`，仅 warning → `0`，操作错误 → `1`）。

它是状态摘要，不是完整 owner approval inbox：blocked 与 pending gate 只显示原值，不会被翻译成"owner 必须批准"。文本与 JSON 从同一份结果渲染，JSON v1 恒含 `schema_version/target/focus/summary/tasks/findings` 键。`status` 不写目标、不访网、不执行文档命令。

### 修订协议

如果要改 Trellium 本身，只修改：

```text
init/INIT.md
init/protocol/*
```

当前仓库里的 `vault/`、`app/` 和测试骨架可以用来验证协议是否合理，但它们不是协议源。根目录 `skills/` 是从协议源提炼出的可分发 Skill 包，修改协议后应同步检查它是否仍与 `init/` 对齐。

修改 `init/` 后生成中英文 Skill 内的权威协议快照：

```bash
python3 scripts/sync-skills.py
```

只检查是否存在漂移，不写文件：

```bash
python3 scripts/sync-skills.py --check
```

该脚本只用于本仓库的发布维护，不是 Skill 用户的安装依赖。CI 会运行相同检查。`references/protocol-source/` 完全由脚本维护；`SKILL.md`、精简的 `references/protocol-model.md` 和 `assets/templates/` 仍需在协议行为变化时人工审查和调整。同步脚本保证协议源进入安装包，但不会假装自动完成中英文语义翻译或模板设计。

修改会影响已接入项目的协议模板时，同步三件事：`scripts/trellium.py` 的 `FILE_ROLES`（新增或删除下发文件时）、`init/MIGRATIONS.md`（追加迁移条目）、`init/VERSION`（按需升版本）。发布供 `--fetch` 使用的版本时打 tag：`git tag <版本号> && git push origin <版本号>`（版本号与 `init/VERSION` 一致）。

## 协议理念

### 任务契约优先

Agent 不按身份获得信任，而是按任务契约获得授权，并按验收标准关闭任务。

任务契约包含：

- 目标和范围；
- 明确不做什么；
- 必要上下文；
- 授权等级；
- 允许和禁止的修改；
- 验收标准；
- 必要验证；
- 记忆更新和交接要求。

### Vault 作为项目记忆

协议会在目标项目中生成 `vault/`，用于承载：

- 项目定位；
- 当前运行态；
- 治理规则；
- 长期决策；
- 任务记录；
- 交接信息；
- 协作偏好。

这样新 Agent、不同模型或不同工具进入项目时，可以从文件恢复上下文，而不是依赖聊天记录。

### 记忆压缩（Compact）

热文件（runtime、handoff、decisions）有明确预算线。预算超出在 `trellium.py check` 中呈现为仓库健康 warning：任务照常验收，不自动触发压缩、不产生额外提交；压缩作为独立 maintenance 动作，仅在用户显式要求、独立 maintenance 任务或任务契约明确包含时执行，流程为五阶段（测量→分类→重组→校验→记录）：runtime 重写而非删减，handoff 仅保留真实中断且非可推导的 transient delta（消费即删，删除不视为信息损失），decisions 超阈值索引化（正文迁入 `vault/decisions/`，默认只读索引）。Superseded/Merged/Expired 等语义判定只出提案，由用户批量确认——压缩永远是零信息损失的重组，不是删除。压缩产出只含 `vault/` 变更的独立提交，可随时回滚。

治理文件（governance、collaboration）由事件驱动激活：升级事件与压缩审查产出治理修订提案，协作偏好在任务收尾被捕获。默认读取路径分级：`index.md` 内置任务与授权速查表，完整 `governance.md` 仅 Level B/C 或判定模糊时读取。

### 可迁移，而不是复制沙盒

不要把当前仓库的生成物整体复制到新项目。

使用完整协议源时，正确方式是：

1. 迁移或引用 `init/`；
2. 让 Agent 读取 `init/INIT.md`；
3. 按协议在目标项目中生成属于它自己的协作层；
4. 根据目标项目实际情况更新 `vault/`、`skills/` 和 profile 产物。

使用 Skill 包时，正确方式是：

1. 安装或复制 `skills/trellium-zh/` 或 `skills/trellium/`；
2. 在目标项目调用该 Skill；
3. 让 Skill 根据内置模板生成目标项目自己的 `AGENTS.md`、`vault/` 和 `skills/agent-task/`。

## 当前状态

本仓库仍处于协议设计和初始化脚手架迭代阶段。

当前重点是打磨 `init/` 和 `skills/`：前者作为协议源，后者作为可安装 Skill 分发包。根目录中的其他生成物主要用于验证协议是否合理。

## 本地验证

当前沙盒带有最小 Python 骨架，用于验证初始化流程：

```bash
uv run pytest
```

这不代表 Trellium 绑定 Python。Python 和 Go profile 只是当前已有的项目类型示例。

## 提交边界

如果目标是发布或迁移 Trellium 协议，提交内容应优先限制在：

```text
init/
skills/
README.md
scripts/
```

除非明确需要更新当前沙盒状态，否则不要把 `vault/`、`app/`、`tests/` 或目标项目生成的 `skills/agent-task/` 等产物作为协议源提交。根目录 `skills/trellium*` 是分发包，可以随协议变化同步提交。
