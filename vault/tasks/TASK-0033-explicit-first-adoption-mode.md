# TASK-0033 - 首次项目接入明确选择存储模式

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0033",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "delivery-accepted",
  "gates": {
    "implementation": "passed",
    "behavioral_verification": "passed",
    "regression": "passed",
    "review": "passed",
    "owner_review": "passed"
  }
}
-->

## Objective

首次给项目接入 Trellium 时，storage 未明确便询问并等待回答；消除未回答按 Local 写入的 fallback，明确选择或已有有效 policy 则复用。

## Scope

双语 SKILL、60/70 canonical 与相关 storage 摘要、protocol-model、MIGRATIONS 未发布条目和自动同步快照；D-0017 替代 D-0012 的未指定 fallback，仍推荐 Local。未答可只读扫描，任何目标写入（含 TASK 契约）前停下；已有选择不重复问，已有项目缺失/无效/冲突 policy 先澄清，升级不自动迁移。

Out of scope：个人习惯、Go Profile 漏路由修复、安装脚本/CLI/schema/模板 policy 默认值、切换本仓 tracked、真实目标接入或 History、更新本机已发布包、VERSION/tag/commit/push。

## Context Required

AGENTS、index/runtime/project/governance、Trellium Work、skill-creator、Comment Policy、D-0012 和接入问答评估；双语 SKILL/reference、60/70、10-vault。

## Capability Tags

skills, governance, onboarding, storage, privacy

## Authority

Allowed：Owner 在评估后明确“同意”，授权所述必答项与复用规则实施；仓库内限定修改与隔离临时 fixture 验证。skill-creator 的 Independent Forward-Testing 用于隐私相关的 Agent 决策验证，评估 Agent 只操作临时项目，不接触真实目标或发送真实提问。

Requires approval：改默认推荐、扩展 CLI/schema、模式迁移、真实安装/发布/commit/push、Owner acceptance。

Forbidden：未答写入、超时当回答、重复索要已有模式、静默覆盖本地工作区、变更已发布 tag、关键词检查冒充对话行为证据。

## Acceptance Criteria

- [x] canonical 与双语入口/摘要没有当前有效的未指定 Local 写入 fallback。（选择门位于 70；60/10-vault 同步改写；残留命中仅在已发布 2026.09.9 历史节，不属当前有效文字）
- [x] 未指定 storage 的首次接入提问并等待；只读操作允许，目标写入为零。（四个等待用例冻结快照逐字节未变：文件 hash + Git index/HEAD/exclude，父 Agent 独立核对 38/38 PASS）
- [x] 明确的 Private/Local/Tracked 选择复用，目标 policy 与 Git 边界相符。（三模式用例：policy 匹配、Private index/HEAD 保持且 project-id ignored、Local 窄 ignore 生效、Tracked 无自动身份；trace 记录未重复询问）
- [x] 已有有效 policy 的升级保留模式；缺失/无效/冲突 policy 写入前澄清。（valid-existing-private：policy/UUID/exclude/project 数据全保留；三个需澄清用例停在提问等待、零写入）
- [x] 包安装与项目接入区分，无全局 storage；独立行为证据不改变真实用户/项目。（package-only 安装与源包 byte-identical，无项目写入；评估仅用临时目标）
- [x] 回归、同步、仓库检查与范围审查完成，如实披露已有失败/未提交风险。（冻结回归 284/283+预存 ancestor-swap FAIL 已披露；sync in sync、check 0 errors/1 warning（本 TASK 未提交）、diff clean；限制见 RESULTS.md）
- [x] Owner 接受交付。（2026-10-01：“你验收通过，我就通过”；Codex review 已通过。）

## Verification

在修改前冻结输入与判定标准：isolated fixture、实际目标 snapshot/Git index/HEAD/exclude 检查；未指定选择只读并记录问题，明确选择按对应边界接入；已有 policy 进行只读 diff/升级，缺失/无效/冲突停止写入。评估输入只含用户请求、Skill 和原始项目，不提供预期答案或修复结论；测试 harness 以文件记录用户问题，不发送真实 UI 消息。两侧内容一致性与 frontmatter 校验；四模块回归、sync --check、check/status、diff --check。既有 ancestor-swap 环境失败不称全量绿。

## Execution Record

- 2026-10-01：接收 Owner 同意，创建契约；既有未提交验证/讨论资料已记录 hashes，所有实现变更单独归因到本任务。Go Profile 发现和 TASK-0032 acceptance 不混入。
- Owner要求先交执行计划并指出18分钟等待；已中断完整三模式接入评估，保留部分trace/fixture，不记整组通过。[收敛后的执行计划](../../docs/plans/2026-10-01-first-adoption-mode.md)先交Owner审阅；后续仅核对已有证据与具体缺口，不重复完整接入/治理/提交/升级演练。当前未commit/push/tag或更新本机包。
- 2026-10-01（PI，verification round）：按计划步骤 2–3 完成收敛核对。从 develop 建 `task-0033-explicit-first-adoption-mode` 分支（携带未提交基线）；以 `audit_targets.py` 对冻结现场 `/private/tmp/trellium-storage-choice-20261001/` 独立重跑：38/38 全 PASS——四个等待用例目标零写入（文件 hash + Git index/HEAD/exclude 逐项比对），三模式 policy/Git 边界/身份绑定正确，既有 Private 全保留，包安装 byte-identical。三 explicit 用例中断点在选择门之后（治理/定制阶段），核心门行为已由冻结现场证实，不重跑完整流程。残留 fallback 文字仅存在于已发布 2026.09.9 历史节（不改写历史）。核对记录写入 `docs/evals/explicit-storage-choice-2026-10/RESULTS.md`（含限制：单次观察、PyYAML 缺失替代校验、回归沿用冻结 284/283 证据、测试对象为工作树包非发布包）。一致性收尾：sync in sync、check 0 errors/1 warning（本 TASK 未提交）、diff clean；未 commit/push/tag，未触碰 owner 未提交资料与其它 TASK。停 ready_for_review 等 owner 验收。

- 2026-10-01（Codex review）：核对 canonical、双语入口/摘要、决策与任务边界，未发现阻塞问题。独立重跑审计 38/38 PASS；核对四个等待用例的提问/停止记录、三明确模式 questions=[]、既有 Private 升级仅询问合并而不重问模式；两侧冻结测试包均与当前工作树逐文件 hash 一致。sync --check、check（0 errors/1 TASK 未提交 warning）、status（0 unresolved）、diff --check 通过。沿用已披露的 284 项回归（283 PASS/1 预存 FAIL），未宣称全量绿；单次行为观察、临时原始证据与替代 YAML 校验限制保留。review gate passed，Owner acceptance 仍 pending；不修改生命周期、不 commit/push/tag/重装。

- 2026-10-01（Owner acceptance）：Owner 明确接受已通过 Codex review 的交付，owner_review passed、lifecycle accepted，验收项全部完成。本次接受不包含 commit/push/tag/重装授权；变更仍为未发布工作树内容，Go Profile 入口修复另行处理。tracked 模式不触发外部 History retention。

- 2026-10-01（发布授权）：Owner 后续明确“push吧”，授权仅提交并推送本任务交付到当前任务分支。保留 TASK-0032、Go Profile 取证与其他既有未提交资料；共享 memory 文件只暂存本任务相关变化。此授权不包含合并 develop、新 tag 或本机重装。

## Memory Updates

D-0017 记录已同意的接入选择规则并保留 D-0012 历史推理；runtime 更新规则与导航，collaboration 保留本次范围偏好。tracked task，Durable knowledge disposition: not_applicable。

## Handoff Requirement

TASK、Git/工作区及落盘证据可推导现场；无真实中断 transient delta 不写 handoff。
