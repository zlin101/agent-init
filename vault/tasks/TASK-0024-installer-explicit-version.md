# TASK-0024 - Installer explicit-version contract

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0024",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-review-passed",
  "gates": {
    "implementation": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

公开安装契约与 tag-only 发布策略一致：`install.sh` 网络安装强制显式 `--version <tag>`，无版本时在任何联网动作前 fail-closed；移除 latest-release 解析；本地 `--source` 安装不需要版本；不实现 latest-tag resolver，不改 `trellium.py --fetch` 的支持范围与行为；修正 README 中 H1 前的 runtime projection 漂移描述。

## Scope

### In Scope

- `scripts/install.sh`：无 `--version` 的网络安装在任何联网前失败并输出明确用法；删除 `resolve_latest_version`；header/usage 更新。
- `scripts/test_install_sh.py`：无版本网络安装 fail-closed 红测（假 `curl` 注入）。
- 中英文 README 安装段：显式版本示例、移除 latest-fallback 语义。
- 双语 Skill `--fetch` 范围限定与 canonical memory 收口（review-driven）：双语 SKILL.md、`vault/decisions.md`、`vault/decisions/D-0013-tag-only-releases.md`、`vault/runtime.md` 簿记。
- README.en H1 漂移修正（runtime projection / Active Tasks / `TASK_RUNTIME_*` 描述）与双语 README `--fetch` 范围限定（adopt/diff/upgrade）。
- 窄回归测试：README 契约（无 H1 漂移措辞、`--fetch` 范围正确）与双语 Skill 命令 smoke（profile argv 透传冻结）。

### Out of Scope

- latest-tag resolver、fetch-version、缓存签名、任何新 CLI 参数。
- `trellium.py --fetch` 行为与支持范围变更（代码真相：仅 adopt/diff/upgrade 支持）。
- Version bump、tag、Release、push。
- H1/H2/TASK-0019 既有内容与 owner-local 排除物。

## Context Required

- `AGENTS.md`
- `vault/runtime.md`
- `scripts/install.sh`
- `scripts/test_install_sh.py`
- 双语 README 安装段与 check/status 章节
- `vault/decisions/D-0013-tag-only-releases.md`

## Capability Tags

- installer
- testing
- documentation

## Authority

Allowed:

- 修改 `scripts/install.sh`、`scripts/test_install_sh.py`、`scripts/test_trellium.py` 契约测试与双语 README 安装段/`--fetch` 范围描述。
- 修改双语 SKILL.md 的 `--fetch` 范围描述与 canonical memory 簿记（`vault/decisions.md`、`vault/decisions/D-0013-tag-only-releases.md` 注记、`vault/runtime.md` Constraints/Known Risks/Next Steps）。
- 运行 installer 测试、契约测试与只读检查。

Requires Approval:

- accepted、push、tag、Release。

Forbidden:

- 重新引入任何 latest-release 解析或联网 fallback。
- 修改 `trellium.py --fetch` 的行为、支持范围或 argparse。
- 触碰 owner-local 排除物（`vault/.agent-init.json` 修改、`docs/engineering/`）。

## Acceptance Criteria

- [x] 无 `--version` 的网络安装在任何联网动作前 fail-closed：exit 1、stderr 含 `--version` 指引；假 `curl` 注入证明零 curl 调用。
- [x] `resolve_latest_version` 及一切 latest-release 解析代码移除；header/usage 不再声称默认解析。
- [x] `--source` 安装不需要版本且行为不变（既有测试保持绿）。
- [x] 双语 README 安装段显式版本；无“默认/回退解析 latest”语义。
- [x] README.en 的 runtime projection / Active Tasks / `TASK_RUNTIME_*` 漂移描述清除，H1 现实描述（status 直读 TASK 状态块）在位。
- [x] `--fetch` 范围在双语 README、双语 SKILL.md 与 70 号模块均为 adopt/diff/upgrade，与 argparse 一致（round 1 P1-1 扩展）。
- [x] canonical memory 与 TASK-0024 后现实一致：D-0013 Impact、decisions 索引行、runtime Constraints/Known Risks/Next Steps（round 1 P1-2）。
- [x] 全量测试、check 0/0、`git diff --check` 通过。

## Verification

Required:

```bash
python3 -m unittest scripts.test_install_sh
python3 -m unittest scripts.test_trellium.ReadmeContractTest
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
git diff --check
```

Completed:

- `install.sh`：移除 `resolve_latest_version`；无 `--version` 的网络安装在任何联网前 fail-closed（exit 1 + 显式指引）；header/usage 更新；`--source` 不需要版本。
- 红测先行：`test_network_install_without_version_fails_closed`（PATH 注入记录调用的假 `curl`，断言调用日志不存在——真证明零联网；exit 1、stderr 含 `--version` 指引）。
- 双语 README 安装段：en 一行安装补 `--version 2026.09.9`、示例与三件事描述改为显式版本两步；zh fallback 句改为移除说明。
- README.en H1 漂移修正：runtime projection / Active Tasks / `TASK_RUNTIME_*` 描述重写为 H1 现实（runtime.md 仅 project-global + Focus；status 直读 TASK 状态块；fresh clone 缺失 = storage contract）；unresolved 示例改用现行 finding codes；policy bullet 补 private。
- `--fetch` 范围限定：README.en/README.md/70 号模块改为 adopt/diff/upgrade（与 argparse 父级一致）。
- 新增 `ReadmeContractTest`：冻结 H1 措辞禁入与 `--fetch` 范围。

Checks run:

- `scripts.test_install_sh` 7/7 OK；`ReadmeContractTest` 2/2 OK；全量 OK exit 0；sync `--check` in sync；嵌入副本 byte-identical；check 0/0；`git diff --check` 干净。

## Execution Record

### 2026-09-29 - Agent: PI — review round 1 rework（REQUEST_CHANGES：3 P1 + 2 P2）

Changes made:

- P1-1：双语 Skill 的 `--fetch` 契约改为 adopt/diff/upgrade（原“any command/任何命令”与 argparse 真相不符）；`ReadmeContractTest` 扩展到两份 SKILL.md（禁“any command/任何命令加”，须含 adopt/diff/upgrade）。
- P1-2：canonical memory 按当前事实收口——D-0013 Impact 改为“TASK-0024 已移除该解析，tag-only 契约由工具强制执行”；decisions 索引行同步；runtime Constraints 与 Known Risks 的 releases/latest 陈述替换为 fail-closed 现实；Next Steps 更新为 Phase 0-3 完成、TASK-0019/TASK-0024 待 review。
- P1-3：TASK-0024 补全 Level C 契约——Context Required、Capability Tags、Authority（Allowed/Requires/Forbidden 含不重引 resolver 等禁令）、逐项 Acceptance Criteria（7 条）、Handoff Requirement。
- P2-4：零联网红测改为 PATH 注入记录调用的假 `curl`，断言调用日志不存在（真证明零 curl 调用，而非仅 stderr 无 http）。
- P2-5：Execution Record 提交哈希更正为 `1380d6f`（amend 后）；移除残留“（待实施）”占位。

Checks run:

- `scripts.test_install_sh` 7/7 OK（含假 curl 零调用断言）；手动无版本安装 exit 1 + 指引输出；`ReadmeContractTest` 全绿；全量 OK exit 0。

Next action:

- Codex 复验本轮 rework。

### 2026-09-29 - Agent: PI — M1 installer + M2 docs complete（ready_for_review）

Context read:

- Owner 收敛计划 Phase 3；`scripts/install.sh` 全文；`scripts/test_install_sh.py` harness；双语 README 安装段与 check/status 章节；`trellium.py` argparse（`content_options` 仅挂 adopt/diff/upgrade）。

Changes made:

- 见 Completed。两笔提交：installer 契约（`6b6747a`）、README.en H1 漂移 + `--fetch` 范围 + 窄回归测试（`1380d6f`，amend 后哈希）。

Checks run:

- 见 Completed。

Review and reflection:

- e2e 网络安装测试不可离线确定，仅红测 fail-closed 分支；`--fetch` 范围以 argparse `parents=[content_options]` 为代码真相。

Risks:

- 无 handoff。

Next action:

- Codex/owner 复验；通过后进入收敛计划 Phase 4（TASK-0025）。

## Handoff Requirement

仅真实中断且存在非可推导 transient delta 时写三小节 handoff；否则不创建。milestone、installer 契约状态与残留 finding 均可从 TASK、Git 与测试恢复，不得进入 handoff；禁止把部分安装契约描述为完成。

## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable（tracked task）
