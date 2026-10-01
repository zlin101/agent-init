# 15 - Vault 记忆压缩

## 定位

本模块定义热文件的记忆生命周期和压缩（Compact）机制。它回答：热文件何时超出健康预算、压缩如何执行、哪些操作 Agent 可以自主做、哪些必须留给用户判断。

它补充 `10-vault.md`，不改变 `20-governance.md` 的授权和验收规则。

## 记忆分层

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；有预算线；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md`、`parked.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

不变量：压缩不直接修改治理文件与结构文件。

## 预算线

项目当前预算的唯一来源是 `vault/index.md` 的 `trellium-policy` 策略块（见 `10-vault.md`）。以下数字是初始化默认值：策略块缺失时供人工压缩判断使用；`trellium.py check` 不用它们冒充项目策略——只做测量，只对策略块中显式配置的阈值报超限。

初始化默认值：

- `vault/runtime.md` 超过 120 行，或 Recent Changes 超过 10 条。
- `vault/handoff.md` 超过 3 条交接或超过 100 行。
- `vault/decisions.md` 超过 150 行或超过 8 条完整决策记录；首次超出时执行索引化拆分。
- `vault/parked.md` 超过 60 行或超过 20 条条目；执行清理提案。
- `vault/tasks/` 当前任务文件（不含 `archive/`、review 台账与已关闭任务）超过 40 个；执行里程碑归档。

## 触发时机

压缩是独立 maintenance 动作，由显式意图触发；普通预算超出本身不是触发器：

- 用户显式要求压缩（例如 "compact vault"）。
- 独立 maintenance TASK 或当前 TASK 的验收标准明确包含压缩。
- 正确性恢复需要：热文件结构损坏导致 canonical 状态不可读或不可解析。

trellium-work 收尾检测到预算超出（`trellium.py check` 的 `BUDGET_EXCEEDED` warning）只报告为仓库健康信号，不自动触发压缩，也不扩大当前 TASK 的 scope。

## 压缩流程

五个阶段，顺序执行：

1. **测量**：运行预算线检查，列出超出的文件。
2. **分类**：对超出文件逐条分类；同时交叉核对治理文件与现实是否漂移（`governance.md` 的必要检查 vs `runtime.md` 实际命令；任务等级边界 vs 实际任务分布），漂移只形成提案。
3. **重组**：执行各文件的压缩算法；语义判定单独成批等用户确认。
4. **校验**：运行校验命令清单，确认全部不变量成立。
5. **记录**：在 `runtime.md` Recent Changes 写一行；形成独立 git 提交；核对 `project.md` 当前阶段与 `runtime.md` 一致，不一致时提出修订。

## 各文件压缩算法

### runtime.md：重写而非删减

以"新会话冷启动需要什么"为唯一标准生成全新文件：当前阶段、可选导航 Focus、当前约束、必要检查、已知风险、下一步。TASK inventory 与状态直接从 `vault/tasks/*` 的状态块读取，不复制进 runtime。

旧内容分流：

- 进行中的进展保留；
- 暂停且暂不推进的任务：降级为 `parked.md` 条目（含重启触发器）；
- 已完成的进展压缩为一行进 Recent Changes，执行历史已在 `tasks/*`；
- Recent Changes 超过 10 条时，老条目并入对应任务文件的 Execution Record 或压缩为一行；
- 长期结论迁入 `decisions.md`。

### handoff.md：消费即删

- 每条是真实中断留下的 transient delta（三小节：Why interrupted / Transient context not captured elsewhere / Exact resume point）。
- 恢复者消费 delta 后删除该条目；过期未消费的条目，在任何 durable 结论已落入 canonical 位置（decisions/TASK）后可直接删除。禁止把 handoff 内容整体搬进 TASK Execution Record 或其他新文档；handoff 是瞬态上下文，删除不视为信息损失。
- 无在途中断时恢复为模板态；正常完成、等待 acceptance 或普通 review 产生的条目属于误写，直接删除。

### parked.md：只出清理提案

- 条目由挂起/重启事件驱动增删，压缩不主动改写。
- 超出预算线（60 行或 20 条）时，输出候选清单：每条含 P-xxxx、建议去向（`details/parked-archive.md` 归档 / 保持）、一句话理由。
- 用户确认前条目一律保留；Agent 不得删除条目。确认后的归档是零信息损失搬运。

### decisions.md：生命周期加索引化

决策状态四态：

- `Active`
- `Superseded by D-xxxx`：被更新决策取代。
- `Merged into D-xxxx`：与同类决策合并。
- `Expired`：前提已消失。

单文件阶段：按现有模板记录，每条标注状态，默认 `Active`。

索引化拆分（首次超过预算线时执行）：

- `vault/decisions.md` 变为纯索引，每条 1-2 行：`D-xxxx · 标题 · 状态 · 一句话实质 · 日期`。
- 完整正文迁入 `vault/decisions/D-xxxx-slug.md`，文件内保留状态字段。
- ID 顺序分配：现有最大编号加一。
- 默认只读索引；需要完整背景时读单条文件。

### tasks/：里程碑归档

- 状态为 Accepted 或 Superseded 且早于最近里程碑的任务文件移入 `vault/tasks/archive/`。
- 纯移动，不修改内容。

## 语义与非语义操作分离

这是压缩安全性的核心。

非语义操作，Agent 可自主执行：

- 正文搬运（decisions 索引化、任务归档）；
- 建立与维护索引；
- 状态标注为 `Active`；
- handoff 已吸收内容的删除。

语义操作，Agent 只能提案，由用户批量确认：

- 判定 `Superseded by D-xxxx`；
- 判定 `Merged into D-xxxx`；
- 判定 `Expired`；
- 判定 parked 条目归档或清理。

提案格式：候选清单，每条含决策 ID、建议状态、一句话理由。未确认的一律保持 `Active`。

执行拆批：

1. 非语义部分先执行并提交；
2. 语义清单经用户确认后作为第二批提交。

## 校验清单

压缩后必须运行并确认：

```bash
wc -l vault/runtime.md vault/handoff.md vault/decisions.md vault/parked.md
```

- 各热文件回到预算内。

```bash
grep -o "D-[0-9][0-9][0-9][0-9]" vault/decisions.md | sort -u
ls vault/decisions/
```

- 索引与目录一一对应：索引无悬挂，目录无孤儿。
- 压缩前的每条决策在压缩后索引中出现（无 Active 丢失）。
- `runtime.md` 的 Focus 若指向不存在的 TASK，只报告 navigation unresolved；TASK lifecycle 仍完全由任务状态块决定。

```bash
git diff --stat HEAD
```

- 本次提交只包含 `vault/` 变更。

## git 安全

- 前置：`vault/` 无未提交变更；否则先提交或中止。压缩永远从干净基线开始。
- 校验失败：恢复 `vault/`（`git checkout -- vault/`），报告失败的不变量，不产生提交。
- 压缩产出独立提交，任意时刻可 `git revert`。

## 任务等级映射

- 例行压缩（纯搬运、无首次索引化、无语义批次）：Level A，在 `runtime.md` 记一行。
- 结构性压缩（decisions 首次索引化、含语义合并批次）：Level B，建立任务文件记录批次内容。
- governance 修订提案被用户接受后的治理变更：Level C，按 `20-governance.md` 执行。

## 治理文件的激活回路

压缩不修改治理文件，但分类阶段必须产出提案：

- `governance.md` 漂移（必要检查过时、等级边界与实际不符、升级规则空白）：输出修订提案清单，按 Level C 处理。
- `collaboration.md`：协作信号由 trellium-work 工作流在任务收尾时捕获（见 `90-collaboration-profile.md`），压缩不做额外处理。
- `project.md`：记录阶段核对当前阶段与 `runtime.md` 一致；不一致时提出修订。

## 反模式

- 把压缩当作删除：任何"判断不重要然后丢弃"的操作都不属于压缩。
- 语义判定不打提案直接执行。
- 压缩提交混入非 vault 变更。
- 在 `vault/` 有未提交变更时开始压缩。
- 改写归档区文件（归档区只增）。
