# TASK-0024 - Installer explicit-version contract

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0024",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "M1-installer-M2-docs-complete-awaiting-review",
  "gates": {
    "implementation": "passed",
    "distribution_sync": "passed",
    "review": "pending"
  }
}
-->

## Objective

公开安装契约与 tag-only 发布策略一致：`install.sh` 网络安装强制显式 `--version <tag>`，无版本时在任何联网动作前 fail-closed；移除 latest-release 解析；本地 `--source` 安装不需要版本；不实现 latest-tag resolver，不改 `trellium.py --fetch` 的支持范围与行为；修正 README 中 H1 前的 runtime projection 漂移描述。

## Scope

### In Scope

- `scripts/install.sh`：无 `--version` 的网络安装在任何联网前失败并输出明确用法；删除 `resolve_latest_version`；header/usage 更新。
- `scripts/test_install_sh.py`：无版本网络安装 fail-closed 红测。
- 中英文 README 安装段：显式版本示例、移除 latest-fallback 语义。
- README.en H1 漂移修正（runtime projection / Active Tasks / `TASK_RUNTIME_*` 描述）与双语 README `--fetch` 范围限定（adopt/diff/upgrade）。
- 窄回归测试：README 契约（无 H1 漂移措辞、`--fetch` 范围正确）。

### Out of Scope

- latest-tag resolver、fetch-version、缓存签名、任何新 CLI 参数。
- `trellium.py --fetch` 行为与支持范围变更（代码真相：仅 adopt/diff/upgrade 支持）。
- Version bump、tag、Release、push。
- H1/H2/TASK-0019 既有内容与 owner-local 排除物。

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
- 红测先行：`test_network_install_without_version_fails_closed`（断言 exit 1、stderr 含 `--version`、不含任何 URL——证明零联网）。
- 双语 README 安装段：en 一行安装补 `--version 2026.09.9`、示例与三件事描述改为显式版本两步；zh fallback 句改为移除说明。
- README.en H1 漂移修正：runtime projection / Active Tasks / `TASK_RUNTIME_*` 描述重写为 H1 现实（runtime.md 仅 project-global + Focus；status 直读 TASK 状态块；fresh clone 缺失 = storage contract）；unresolved 示例改用现行 finding codes；policy bullet 补 private。
- `--fetch` 范围限定：README.en/README.md/70 号模块改为 adopt/diff/upgrade（与 argparse 父级一致）。
- 新增 `ReadmeContractTest`：冻结 H1 措辞禁入与 `--fetch` 范围。

Checks run:

- `scripts.test_install_sh` 7/7 OK；`ReadmeContractTest` 2/2 OK；全量 OK exit 0；sync `--check` in sync；嵌入副本 byte-identical；check 0/0；`git diff --check` 干净。

## Execution Record

### 2026-09-29 - Agent: PI — M1 installer + M2 docs complete（ready_for_review）

Context read:

- Owner 收敛计划 Phase 3；`scripts/install.sh` 全文；`scripts/test_install_sh.py` harness；双语 README 安装段与 check/status 章节；`trellium.py` argparse（`content_options` 仅挂 adopt/diff/upgrade）。

Changes made:

- 见 Completed。两笔提交：installer 契约（`6b6747a`）、README.en H1 漂移 + `--fetch` 范围 + 窄回归测试（`222f07e`）。

Checks run:

- 见 Completed。

Review and reflection:

- e2e 网络安装测试不可离线确定，仅红测 fail-closed 分支；`--fetch` 范围以 argparse `parents=[content_options]` 为代码真相。

Risks:

- 无 handoff。

Next action:

- Codex/owner 复验；通过后进入收敛计划 Phase 4（TASK-0025）。

（待实施）

## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable（tracked task）
