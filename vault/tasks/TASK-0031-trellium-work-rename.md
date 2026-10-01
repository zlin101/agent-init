# TASK-0031 - 项目工作流改名 Trellium Work

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0031",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "owner-accepted",
  "gates": {
    "implementation": "passed",
    "regression": "passed",
    "distribution_sync": "passed",
    "owner_review": "passed"
  }
}
-->

## Objective

将现有 agent-task starter workflow 改名为 trellium-work / Trellium Work，保持工作内容和 AGENTS.md + vault 的入口职责。安装 Skill trellium / trellium-zh 名称不变。

## Scope

- 新项目目标路径 skills/trellium-work/SKILL.md；本仓工作流与双语不可发现模板同步改名。
- 更新有限 managed paths、stamp 校验兼容、Private preflight/check 边界、现行协议和用户文档。
- 已有项目采用显式 Agent 迁移：保留用户定制、协调旧/新路径、stamp 和 Private exclude；迁移前新版 adopt/upgrade/baseline 明确拒绝写入，旧 stamp 与旧 Private namespace 仍能只读检查。本仓仅迁移工作流及其已追踪 stamp 条目，不改 stamp 其他字段。

Out of scope：独立第二工作 Skill、新的 Agent 发现/安装位置、新 CLI/schema、自动删除旧项目内容、已安装用户级 Skill 修改、默认 storage、History 行为、Git stage/commit/push/tag、版本号递增。

## Context Required

AGENTS、index/runtime/governance/project、当前 starter workflow、skill-creator、Python 工程约束及 Comment Policy、D-0009、adopt/diff/upgrade 与 Private 契约。

## Capability Tags

skill, compatibility, privacy, migration, python, documentation

## Authority

Allowed：Owner 询问 trellium-work 后同意完整命名方案，授权上述改名及必要兼容迁移。本仓 root stamp 的唯一工作流条目随路径迁移，其余 adoption/project identity 信息逐字保持。

追加授权（2026-10-01）：Owner 明确确认“你通过，那我这里也通过，push吧”，接受当前交付并授权 stage/commit/push develop。本次不创建或移动 tag、不递增版本，TASK-0027 的 owner_review 独立保留。

Requires approval：新 tag 发布、扩大到用户级安装路径或新的项目 Skill 发现架构、真实其他项目迁移、owner 接受。

Forbidden：覆盖定制、留下两个工作流入口、放宽 Private ignore、伪造独立复审、修改历史实验和已接受任务。

## Acceptance Criteria

- [x] 新项目和两种分发包生成唯一 trellium-work 工作流，name、标题、目录一致。
- [x] 模板保持不可发现文件名；安装 Skill 名称不变。
- [x] 旧 stamp/Private 项目可只读 check；含旧工作流的写操作零写入拒绝并给出迁移指引。
- [x] 显式迁移保留定制、stamp/UUID 及 Private 边界；迁移后 upgrade 的 proposal 保护有效。
- [x] forced-add 新旧工作流 namespaces 可检测，两个 namespaces 的 tracked 碰撞均拒绝 Private 接入。
- [x] 回归、sync/check/status/diff、Skill 结构和文档检查如实记录。
- [x] Owner 验收。

## Verification

聚焦命名/legacy migration/Private 边界及双语分发 tests；完整四模块；sync --check；check/status/diff --check；quick_validate；文档链接和新文件 whitespace。预存 macOS ancestor-swap 失败与新路径未提交的 HEAD Gate 分别披露，不绕过 Git Gate。必要时 Linux 非 root 运行聚焦；全部目标隔离临时目录，不访问真实 History。

## Execution Record

- 2026-10-01：基线 develop 830f7b0 / tag 2026.10.0，工作区干净；Owner 同意 trellium-work 命名。查阅 D-0009：其 No-Go 针对新增项目发现入口，本次只命名既有 starter，不扩大架构。

- 实现目标/模板/name/标题改名；legacy stamp 有限兼容与显式迁移守卫，Private 基于 stamp 选择原/新 exclude namespace，preflight/forced-add 同时覆盖两者。重复 adopt --force / upgrade --complete / 无 stamp baseline 的旧路径拒绝均在写前发生。
- 本仓只移动 starter 并协调原 stamp 的单一 workflow entry；其他条目及字段逐字段比较不变。迁移后 observed baseline 保护现有定制，不更新协议版本、不调用真实 History、不修改已安装用户级包。
- [最终验证](../../docs/evals/work-skill-rename-2026-10/RESULTS.md)：macOS 聚焦 52 PASS；Linux 非 root 聚焦 55 PASS；macOS 全量 284 tests / 283 PASS / 1 同一预存 FAIL，范围内 regression passed 不代表全量绿。新增 10 项迁移/安全测试，双语实际生成断言已验证。
- 隔离临时提交 + fresh clone check 0/0、status exit 0；实际仓库因改名未提交 check/status 2 HEAD Gate errors + 1 新 TASK warning，未绕过。sync/diff/AST/文档和替代 YAML 结构校验通过；quick_validate 缺 PyYAML 的原失败已披露，无依赖变更。
- 两轮自检分别核对兼容/privacy 覆盖及命名最小性，未使用独立 reviewer；停在 ready_for_review，owner_review pending，未 stage/commit/push/tag。没有实际中断，不更新 handoff。

### 2026-10-01 - Owner acceptance / develop push

- Owner 接受交付并授权 push，lifecycle 转 accepted，owner_review passed；没有独立 reviewer，不将 owner 接受描述为独立复审。
- 提交前确认所有实现 fingerprints 与验证记录一致，远端 develop 与本地基线仍同为 830f7b0；只更新接受/交接记录，无产品或测试改动，无须重复同一行为测试。既有 macOS 全量失败与 quick_validate 缺依赖风险保留。
- 本轮提交并推送改名、配套协议、双语分发、root stamp 的单项迁移及全部验证证据；实际提交后必须重跑本仓 check/status，确认两项 HEAD Gate error 消失；git index 不用于绕过检查。版本与 tag 2026.10.0 保持原值，尚无新 tag 发布授权。

## Memory Updates

- D-0016 记录命名和显式迁移；D-0009 原结论保留，追加限定说明。
- runtime 更新全局名称及导航，不保存 TASK 状态投影。
- Durable knowledge disposition: not_applicable（tracked task）。

## Handoff Requirement

工作区、任务和重跑检查可推导，无真实中断 transient delta，不写 handoff。
