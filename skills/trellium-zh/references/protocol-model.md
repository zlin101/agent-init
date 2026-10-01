# Trellium 协议模型

## 目的

Trellium 为软件项目添加持久的协作层。它不是业务框架、角色层级、CI 系统或 LLM 运行时。

核心原则：

> Agent 不按身份获得信任，而是按任务契约获得授权，并且只有通过验收门才能关闭工作。

## 分层

- 入口层：共享的 `AGENTS.md`，以及目标工具仍明确需要时的专属兼容文件；Claude Code 直接读取 `AGENTS.md`。
- 上下文层：`vault/index.md`、`vault/project.md`、`vault/runtime.md` 和可选 `vault/details/*`。
- 治理层：`vault/governance.md` 和 `vault/tasks/*`。
- 决策层：`vault/decisions.md`。
- 交接层：`vault/handoff.md`。
- 工作流层：`skills/*/SKILL.md`。
- Profile 层：只有项目类型明确时才加入语言或框架默认值。

## 必需 Vault 文件

除非目标项目已有等价文件并需要合并，否则创建：

```text
vault/
  index.md
  project.md
  runtime.md
  governance.md
  decisions.md
  handoff.md
  parked.md
  collaboration.md
  tasks/
    README.md
    .gitkeep
```

## 记忆分层与压缩

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；预算线内；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md`、`parked.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新 |
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增 |

预算线：runtime ≤ 120 行（Recent Changes ≤ 10 条）；handoff ≤ 3 条交接或 100 行；decisions ≤ 150 行或 8 条记录；parked ≤ 60 行或 20 条；tasks ≤ 40 个当前任务文件（不含 archive 与 review 台账）。以上是初始化默认值；项目当前预算与 TASK storage 只配置在 `vault/index.md` 的 `trellium-policy` 策略块中。`trellium.py check <target>` 始终测量热文件，只对显式配置的阈值报超限；策略块缺失按 legacy 报告，不用隐藏默认值替代。

只读状态摘要：`trellium.py status <target>`（2026.09.5）直接扫描 canonical TASK 状态块形成 owner 视图——导航 Focus、开放任务分类（draft/active/blocked/ready_for_review，含 authority/slice/gates 原值与任务路径）、closed 只进计数、无法解析的 TASK state 显式列出并附发现码。Focus 只有导航语义；不推断 lifecycle/authority，不冒充 approval inbox，退出码与 `check` 一致（error `2` / 仅 warning `0` / 操作错误 `1`）。

压缩五阶段：测量→分类→重组→校验→记录。非语义操作（搬运、索引、标注 Active、暂停任务降级为 parked 条目）Agent 自主执行；语义判定（Superseded by D-xxxx / Merged into D-xxxx / Expired、parked 清理）只提案，用户批量确认，未确认保持 Active。压缩是只含 `vault/` 变更的独立提交。策略块配置的预算超出在 `trellium.py check` 中只是仓库健康 warning；压缩本身是显式意图触发的独立 maintenance 动作，不是自动的任务收尾步骤。

决策索引化：decisions.md 变纯索引，正文入 `vault/decisions/D-xxxx-slug.md`。索引原则：增长进目录，读取走索引。

读取契约由 `30-agent-entry.md` 定义、项目入口文件实现（默认集合与全部条件触发见该文件）；本参考不重复读取流程。

## 状态块与策略块

两个带版本的小 JSON 块承载"当前状态事实"，其余内容保持 Markdown。

`trellium-task-state` 位于 Level B/C 任务标题之后。必填字段：`schema_version`（整数 `1`）、`task_id`（`TASK-NNNN`，与文件名一致）、`level`（`B | C`）、`authority_level`（整数 0..4）、`lifecycle`。可选：`current_slice`（非空字符串）与 `gates`（开放 Gate ID → `pending | in_progress | passed | partial | blocked | not_authorized | not_applicable`）。未定义字段非法。它是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner，不授予批准。没有状态块的任务文件是 legacy（报告、不猜测）；review 台账与 `tasks/archive/` 不带状态块。

`trellium-policy` 位于 `vault/index.md` 开头。必填：`schema_version`（`2`）与 `storage_mode`（`tracked | local | private`）；可选 `budgets`（各热文件一项）。legacy schema v1（`task_storage: tracked | local`）继续可解析，不自动改写。它是项目预算与 storage 的唯一来源。首次接入询问 owner 并推荐/默认 `local`；只有任务文件、review 台账与 archive 不进 Git，协作核心仍 tracked，Accepted 结论必须蒸馏进公开位置。需要共享完整流水时选择 `tracked`。选择 `private` 让目标项目的全部 Trellium managed material 不进 Git，terminal TASK/review 可经本机 History Store 保全：untracked、由 `.git/info/exclude` 的 canonical trellium-private block 精确忽略、反向 privacy Gate 校验，并在 adopt 前运行只读 `private_preflight` 探针（见 70-adoption-flow.md「Private 存储模式」）。local 接入生成窄范围 `vault/tasks/.gitignore`（private 不生成——整个 Vault 已由 private block 覆盖）；工具不自动迁移或 untrack。local 任务进入 `accepted` 前在 Memory Updates 记录 Durable knowledge disposition（`none — <理由>` 或 `distilled — <canonical 目标文件>`；未填写视为 `pending`，不得进入 `ready_for_review`/`accepted`）。fresh clone 中被忽略的 local 任务文件不存在，这是 storage contract；runtime 不提供恢复副本。

## 任务生命周期

`draft | active | blocked | ready_for_review | accepted | superseded`

`trellium-task-state` 状态块是 lifecycle、Authority、当前 slice 与 Gate 结果的唯一持久化 owner；`runtime.md` 不保存 TASK 投影。暂停且暂不推进的工作放 `parked.md`，不是 lifecycle 值。Level A 不持久化 TASK lifecycle，从工作区、Git diff 与测试结果恢复。

## 文件职责

- `vault/index.md`：路由表 + `trellium-policy` 项目策略块；不保存运行态。
- `vault/project.md`：稳定项目目标、范围、边界和当前阶段。
- `vault/runtime.md`：短项目全局当前状态、可选导航 Focus、检查、风险和下一步；Focus 不拥有 task state、Authority 或活跃任务清单。
- `vault/governance.md`：任务等级、授权等级、任务生命周期、任务契约、验收门、升级规则和 handoff。
- `vault/decisions.md`：决策索引与生命周期记录（Active / Superseded / Merged / Expired）；正文拆分后在 `vault/decisions/*`。
- `vault/handoff.md`：仅当真实中断留下非可推导恢复事实时才写入的 transient delta；每条（任务编号或 SESSION）只含三小节——Why interrupted、Transient context not captured elsewhere、Exact resume point；恢复先读 TASK/实时 Git/测试，用 delta 补齐后即删。
- `vault/parked.md`：用户挂起事项冷索引；仅被提及时读取，不进默认读取路径；恢复时升回任务文件。
- `vault/collaboration.md`：不能覆盖硬治理的软协作偏好。
- `vault/tasks/*`：追踪或治理任务的契约、执行记录、验证和关闭说明。
- `skills/*`：可复用 Agent 工作流。

## 任务等级

判定顺序：命中 Level C 风险域 → C；否则中断恢复或协作成本明显较高 → B；否则 → A。规模只提示判断，不单独决定等级。

- Level C，治理任务：命中风险域即治理，一行修改也不例外（安全/隐私、公开 API 或外部契约、持久数据/迁移、部署/生产行为、依赖、成本/配额、架构方向/重大架构决策、治理规则）。记录在任务文件和 `vault/decisions.md`；通常需要用户确认。
- Level B，追踪任务：非 C 风险域但恢复或协作成本明显较高（跨 session、真实 handoff、多 owner、外部系统状态、多阶段 gate、diff/tests 难以恢复的 execution state）。记录在 `vault/tasks/TASK-xxxx-short-title.md`。
- Level A，简单任务：低风险、恢复与协调成本低。默认不持久化 TASK lifecycle，从工作区、Git diff 与测试结果恢复。

## 授权等级

- Authority 0：只读分析。
- Authority 1：低风险局部修改。
- Authority 2：说明边界和检查后的限定范围修改。
- Authority 3：高影响工作需要批准。
- Authority 4：禁止事项，包括保存密钥、伪造验证、未授权破坏性命令和静默覆盖用户改动。

## 任务契约字段

追踪任务和治理任务应包含：

- Objective
- Scope and out of scope
- Context required
- Capability tags
- Authority level（数值由任务状态块承载，不设第二份可编辑副本）
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

## 验收门

不要在满足以下条件前关闭工作：

1. 逐条检查验收标准。
2. 运行必要验证，并记录结果。
3. 适用时同步代码、测试、文档和 vault 记忆。
4. 更新 `vault/runtime.md`。
5. 在 `vault/decisions.md` 记录长期决策。
6. 在任务文件记录未完成工作或风险（不用普通 handoff）。
7. 没有隐藏的高影响变更。

测试通过不等于完成。

## 执行模式

- Plan first：编辑前明确目标、边界、验收、验证、文件和不做范围。
- Context grounded：先读本地项目上下文，再应用通用建议。
- Checkpointable：通过任务文件、runtime、实时 Git/测试让长任务可恢复；仅真实中断且留下非可推导 delta 时另有 transient-delta handoff。
- Human signal：架构、成本、安全、隐私、部署和模糊产品取舍交还用户判断。
- Review ledger：多轮 review 用 `TASK-xxxx-review.md` 台账批量收敛，每轮一次写入替代消息往返；收敛后归档进任务文件。
- Workflow compounding：重复稳定工作流沉淀为聚焦 skill，而不是扩写入口文件。

## 既有项目接入边界

接入模式默认只新增或合并 Agent 协作文件。

默认允许：

- Agent 入口文件
- `vault/`
- `skills/`
- 极短 README 协作说明，但要先说明意图

没有用户明确授权时禁止：

- 业务源码
- 测试
- 依赖和锁文件
- 构建、部署或 CI 文件
- 数据库迁移
- 环境文件
- 大段既有文档重写
- 密钥或凭据

## 协作画像

`vault/collaboration.md` 记录稳定协作偏好和观察模式。它是软画像，不是硬规则。它不能覆盖用户当前指令、Agent 入口文件、治理、任务契约、决策、安全、权限、测试、成本或部署约束。
