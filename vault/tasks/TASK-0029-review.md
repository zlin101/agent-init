# TASK-0029 - Independent Acceptance Review

## Review Basis

- Reviewer: Codex；2026-09-30；owner 请求“验收一下”。
- HEAD: `756c4967d242f78983df8cd3dd81c3b099798ff0`，37 项现有工作区修改；原 Task/POC 是证据与验收契约，正式模块/分发副本是当前审查对象。
- Verdict: **APPROVE**（修复批次 4 独立重审）；F29-001/F29-002/F29-003 fixed、F29-004 resolved，blockers = 0。保留原 P3 与预存 macOS validation residual，不宣称全量 suite 绿；本轮未采用或要求新的 strict profile。
- Round 1 verdict: **REQUEST_CHANGES**。Default-profile loop PASS 不免除 TASK 的冻结 acceptance/verification；原反例与缺证据记录保留为历史。
- Round 2 re-review: Codex；2026-10-01；首修复批次增量重审为 **REQUEST_CHANGES**，当时 F29-001/F29-002 reopened（P1）。独立复核 fixture/输出见 [Round 2 evidence](../../docs/evals/historical-evidence-store-2026-10-rereview/RESULTS.md)，保留为历史。
- Round 4 re-review: Codex；2026-10-01；修复批次 2 为 **REQUEST_CHANGES**，当时仅 F29-002 reopened（P1，损坏 HEAD 文件被误判非仓库）；证据见 [batch 2 evidence](../../docs/evals/historical-evidence-store-2026-10-rereview/batch2-RESULTS.md)，保留为历史。
- Round 6 re-review: Codex；2026-10-01；修复批次 3 为 **REQUEST_CHANGES**，当时仅 F29-002 reopened（P1，metadata lookup 错误被 lexists 吞掉后当作不存在）；证据见 [batch 3 evidence](../../docs/evals/historical-evidence-store-2026-10-rereview/batch3-RESULTS.md)，保留为历史。
- Latest re-review: Codex；2026-10-01；修复批次 4 **APPROVE**，所有独立验收 findings 关闭；最终 fixture/原始 Linux 输出/fingerprints/规模测量见 [batch 4 evidence](../../docs/evals/historical-evidence-store-2026-10-rereview/batch4-RESULTS.md)。review passed；Owner 随后于 2026-10-01 显式接受交付，TASK 已 accepted。
- Fix batch 2 (2026-10-01, PI)：F29-001/F29-002 剩余边界补齐（bootstrap 父级链、零修订结构探针），聚焦测试 +4，状态回 fixed 待 owner 重审；详见各 finding 下的第二轮 Fix/Verification 与 Round 3 Fresh Verification。
- Fix batch 3 (2026-10-01, PI)：F29-002 最后分支——corrupt `.git/HEAD` 的误导性非仓库 stderr；非仓库分类改为结构探测门控（`.git` 条目存在即 unknown），聚焦测试 +1，状态回 fixed 待 owner 重审；详见 F29-002 下第三轮 Fix/Verification 与 Round 4 Fresh Verification。
- 不修产品代码、不 commit/push、不写真实 `~/.trellium/history`；所有反例与 smoke 使用自建 TemporaryDirectory 项目与外部 Store。下面记录的是复现观察，不是物理断电/实际数据丢失实验。

## Findings

### F29-001 · P1 · fixed · Failed ancestor fsync is skipped on retry

- Location: `scripts/history_store.py:89–95`（`_mkdir`），`put` 的父目录准备路径。
- Contract: TASK Historical Store 要求成功响应前保证必要父目录创建持久化，失败后重试重新核验/同步。
- Repro: 新临时 Store root 创建后，注入其父目录 `_sync_dir` 失败；第一次 put 抛 OSError，但 root 已存在。撤销失败并记录第二次 put 的 `_sync_dir` 调用：重试返回 digest、get bytes 正确，但此前失败的 root-parent 从未再同步。`if path.is_dir(): return` 把可见性当作该目录项已持久化；同类问题可发生于其他 ancestor 及协作 writer 的交错。
- Fresh output:

```text
first put: OSError root remains: True
retry returned verified digest: True
retry re-synced previously failed root-parent link: False
retry sync sequence: external-store; external-store/<UUID>;
  external-store/<UUID>/TASK-0029/.pending-<random>;
  external-store/<UUID>/TASK-0029
```

- Impact: 允许在必要 ancestor sync 未成功的情况下确认 retention，后续获授权 cleanup 可以依赖不满足契约的成功结果。Cooperative-writer 假设不免除 fsync 错误处理；不声称已实测断电丢失。
- Required fix/verification: 成功路径包含必要 ancestor links 的同步（包括失败后已存在的目录）；新增 root/project/artifact 父目录首次同步失败→重试的聚焦测试，并覆盖并发创建不能绕过同步。不以新增 journal/index 扩大 scope。
- Fix (2026-09-30, PI)：`Store._sync_namespace(parent)` —— put 成功路径在 per-artifact fsync 后对 artifact/project/root/root.parent 全链重确认（`scripts/history_store.py`）；不再信任“可见即已持久”。
- Verification：`test_retry_reacknowledges_ancestor_links_after_failed_sync`（root-parent/root/project 三级首次同步失败→重试补同步并逐 bytes 核验）+ `test_existing_namespace_is_reacknowledged_on_success`（他人/早期 writer 创建的 namespace 在成功路径仍重同步，并发不绕过）均 PASS；macOS 3.9.6 与 Linux 3.12.3 双组合执行。
- Re-review (2026-10-01, Codex)：以上三个层级与已存在 namespace 已修复，但 `scripts/history_store.py:169–172` 在 `root.parent` 停止。默认 `<home>/.trellium/history` 的 `.trellium` 也需新建时，首次同步 `<home>` 失败后，重试跳过其同步而返回成功。隔离 fixture 在 macOS/Linux 均输出 `retry success = True ; failed parent fsync retried = False`。必须覆盖 root.parent 自身及更高层新建目录项，成功路径重确认所有必要 links；添加此层首次失败→重试与协作创建边界。不把内存中的“本次新建目录”列表当作跨重试/跨 writer 的充分证据，不新增 journal/index。
- Fix (2026-10-01, PI)：`_sync_namespace` 重确认链延伸至 `root.parent.parent`（bootstrap 目录的父级，如 `~/.trellium` 的 dirent 持久化层），固定结构链、不依赖任何 per-put 新建列表，跨重试/跨 writer 一致；`Store.__init__` 新增构造守卫——bootstrap 之上祖先缺失的 root 显式拒绝（`ValueError`），不再对无法有界确认的布局静默报告成功。
- Verification：`test_retry_reacknowledges_bootstrap_parent_after_failed_sync`（`.trellium` 新建 + `<home>` 首次同步失败→重试补同步并逐 bytes 核验）+ `test_bootstrap_parent_link_is_reacknowledged_on_existing_store`（bootstrap 已存在时每次成功仍重同步该 link，覆盖协作 writer 遗留未确认项）+ `test_store_rejects_missing_parent_chain_above_bootstrap` 均 PASS；既有三级 ancestor/已存在 namespace 测试保持 PASS；双组合执行。按 reviewer 复现格式独立复跑：`first put failed, bootstrap visible: True / retry success: True / failed parent fsync retried: True`（Linux 3.12.3 / git 2.39.2 / overlayfs）。

### F29-002 · P1 · fixed · Git-unavailable evidence is treated as unbound

- Location: `scripts/trellium.py:2404–2406`（`_identity_in_head`），`ensure_project_identity` 的 missing-file 首次绑定分支。
- Repro: 临时 adopted local 项目，stamp 尚无 identity 登记，原 `vault/project-id` 已在临时 Git HEAD；删除临时 working-tree identity。Git 正常时 helper 正确拒绝创建。将 `git_run` 注入为 None（不可执行 Git）后，再用 `authorize_create=True` 调用 helper：它创建并登记一个与 HEAD 原 UUID 不同的身份。
- Fresh output:

```text
available Git with HEAD identity: creation refused
unavailable Git: created replacement identity: True
replacement differs from HEAD identity: True
```

- Impact: 未知绑定证据被当成“没有绑定”，违反“已拥有身份缺失须恢复”和“证据查询失败 fail closed”；旧 Store namespace 与新身份分离。首次创建授权不能覆盖恢复门。
- Required fix/verification: 区分已证明无 HEAD/非 Git与操作错误/不可查询，Git 缺失及 rev-parse operational failure 返回 unknown 并拒绝写入；测试必须覆盖 rev-parse 失败，而非只覆盖后续 cat-file 失败。Monorepo prefix 查询也应遵循同一 unknown 边界。
- Fix (2026-09-30, PI)：`_identity_in_head` 重写证据分类（`scripts/trellium.py`）——git_run 返回 None（Git 不可用/不可执行）→ unknown；rev-parse 失败时按 stderr 分类：非仓库/无提交（含 `Needed a single revision`）为可证明无 HEAD，其余 operational failure → unknown；monorepo prefix 改用 `_git_root_prefix_strict`（失败→unknown）。unknown 由 `identity_binding_evidence` 统一拒绝写入。
- Verification：`test_git_unavailable_fails_closed`（HEAD 已含原身份 + Git 不可用 → 拒绝创建）、`test_rev_parse_operational_failure_fails_closed`、`test_monorepo_prefix_failure_fails_closed`、`test_repository_without_commits_has_no_head_evidence`（无提交仓库仍可首次绑定）均 PASS；双组合执行。
- Re-review (2026-10-01, Codex)：Git 不可执行与已测试操作错误已拒绝，但 `scripts/trellium.py:2427–2433` 仍把无法确定 HEAD 的错误字符串当成无提交证明。实际临时仓库先提交 identity、删 working-tree identity，再将 HEAD 指向的 loose ref 内容损坏为 `corrupt ref\n`；Git 2.54.0/2.39.2 均报 `fatal: Needed a single revision`，helper 随后创建并登记不同 UUID。`replacement created = True ; differs from committed identity = True ; registered = True`。需用可核验的 unborn/non-repo 证据区分不存在与不可查询；损坏/不可读 ref、HEAD/object 查询失败均 unknown 且无写入，保留真实无提交正例。不以 stderr substring 单独证明无绑定。
- Fix (2026-10-01, PI)：`_identity_in_head` 删除全部 no-commit stderr 子串分类；HEAD 不可解析时改用结构探针 `git rev-list -n 1 --all`：仅当 Git 自身确认仓库零修订（rc=0 且输出为空）才判可证明 unborn（False）；仓库仍有修订（含 corrupt/unreadable ref）、探针失败或 Git 缺失均返回 unknown 并拒绝写入。非仓库 stderr 分类保留。stderr 不再单独证明无绑定。
- Verification：`test_corrupt_head_reference_fails_closed`（提交身份→删 worktree→loose ref 写 `corrupt ref\n`→`authorize_create=True` 拒绝且无写入）+ `test_rev_parse_operational_failure_fails_closed`（改为有修订仓库中注入 rev-parse 失败，操作失败语义更精确）+ 无提交正例 `test_repository_without_commits_has_no_head_evidence` 保持 PASS；双组合执行。按 reviewer 复现条件独立复跑：rev-parse stderr 含 `Needed a single revision` 时 `replacement created: False`、无替换文件落盘（Linux 3.12.3 / git 2.39.2）。

### F29-003 · P2 · fixed · Identity helper uses a weaker policy parser

- Location: `scripts/trellium.py:2441–2450`（`_require_local_policy_for_identity`）。
- Repro input:

```json
{"schema_version":2,"storage_mode":"private","storage_mode":"local"}
```

- 将此对象放入临时项目唯一 policy comment block。Canonical `check_policy_block` 通过 `parse_block_object` 拒绝 duplicate key，并报 POLICY_INVALID；helper 使用普通 `json.loads` 接受末值 local，随后创建并登记身份。它还循环寻找任一 local block，不要求策略块唯一。
- Fresh output:

```text
canonical checker rejects duplicate key: True
identity helper nevertheless creates: True
```

- Impact: 不能证明 explicit valid local 的策略仍能进入写入路径，checker/helper 对同一 storage policy 的授权判断不一致。
- Required fix/verification: 使用既有严格 policy parser 与唯一块/完整块检查；duplicate key、多个 policy blocks、unterminated block、非对象 JSON 和非法值均须无写入拒绝。无需新增 schema/parser 系统。
- Fix (2026-09-30, PI)：`_require_local_policy_for_identity` 改用 canonical `extract_comment_blocks` + `parse_block_object` + `validate_policy_object`（`scripts/trellium.py`），与 `check_policy_block` 同一严格语义；要求恰好一个 policy block，任何 POLICY_INVALID 类输入直接拒绝，不再循环寻找“任一可用块”。
- Verification：`test_policy_parsing_matches_checker_strictness`（duplicate key / non-object / JSON constant / invalid value / multiple blocks / unterminated，全部无写入拒绝）PASS；双组合执行。
- Re-review (2026-10-01, Codex)：确认使用 canonical parser/validator 与恰好一块规则；macOS/Linux 的该聚焦测试均 PASS，维持 fixed。

### F29-004 · P2 · resolved · Required Linux implementation validation is missing

- Location: TASK-0029 Frozen Design 环境矩阵、Acceptance Criteria 和 Required Verification；当前实现记录明确 Linux / Python 3.12.3 未执行。
- Required evidence: 正式模块七类 failure cases 与已分发调用路径在 Linux / Python 3.12.3 的 fresh 结果，注明 OS/解释器/filesystem；原 disposable POC 13/13 与当前 macOS 结果均不替代此项。
- Resolution: 补跑并保存证据；若 owner 改变验收矩阵，须显式修订契约，不能把缺环境自行降为 residual 或以 loop default profile 豁免。
- Resolution evidence (2026-09-30, PI)：Docker（OrbStack）+ `python:3.12.3` 官方完整镜像（经 daocloud 国内镜像拉取），代码拷入容器本地 overlayfs（非 virtiofs 挂载），以非 root 用户执行（case 7 只读目录前提为非特权写者）：`test_history_store` 17/17 PASS、`ProjectIdentityTest` 16/16 PASS、分发副本 importlib 加载 + TASK+ledger 成组 retain→删 clone→找回 E2E PASS。环境记录：Linux 7.0.14-orbstack aarch64 / Python 3.12.3 / git 2.39.2 / overlayfs。七类 failure cases 与分发调用路径证据已取得。
- Re-review (2026-10-01, Codex)：使用现有镜像、禁用网络、uid 65534、容器本地 overlayfs 独立复跑 17 Store + 16 identity tests（33/33 PASS），两语言分发 E2E 均 PASS；完整输出见 evidence。F29-004 resolved，但这组现有测试通过不消除上面两项额外反例。

## Round 1 Fresh Verification · 2026-09-30（历史）

- `python3 -B -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh scripts.test_history_store`: 245 tests；244 PASS / 1 FAIL，唯一失败 `AgentInitTest.test_keeps_original_target_when_ancestor_is_swapped_after_open` 与本会话实施前干净基线一致。既有失败不作为本次新增缺陷；全量命令结果仍是 FAIL。
- 本次全量中的正式 Store 15 tests 全部通过；上述三个额外隔离反例显示其测试集与 identity 测试集仍有覆盖缺口。
- `python3 -B scripts/sync-skills.py --check`: PASS，双语派生副本 in sync。
- `python3 -B scripts/trellium.py check . --format json`: PASS，0 errors / 0 warnings；预算测量完成，当前 policy 无配置阈值。
- `python3 -B scripts/trellium.py status . --format json`: PASS，TASK-0029 ready_for_review，Focus TASK-0028 resolved。
- `git diff --check`: PASS。
- 两语言 `assets/history_store.py` 用 importlib 不注册 sys.modules 加载，在自建临时 clone 上执行 TASK+ledger retain smoke：第二 artifact 注入写入失败时整组未成功且 source 保留；重试两份成功；删临时 clone 后仅 UUID/artifact id/digest 找回原 bytes，list 校验 source_relative_path。两包均 PASS。此项只验证模块及调用者成组操作，不声称自动完成必要 ledger 发现或 lifecycle/policy 判定。
- Linux 正式验证：NOT RUN。原两份 loop verdict 文件未在本仓找到；owner 提供的 loop 摘要作为历史报告，与本轮 fresh 复现分开。

## Round 2 Fresh Verification · 2026-10-01

- macOS / Python 3.9.6：全量 252 tests，251 PASS / 1 既有 FAIL（14.341 s）；33 聚焦 tests PASS（1.599 s）。全量命令结果仍为 FAIL，预存 ancestor-swap fixture 失败不作为新增 blocker。
- Linux / Python 3.12.3 / overlayfs / non-root：33 聚焦 tests PASS（2.543 s）；两语言分发 E2E PASS。
- 两组均独立复现 F29-001/F29-002 的修复剩余边界；原三个 ancestor 级别、Git 不可用/查询错误/prefix 错误、无提交正例和六类 malformed policy 测试全部通过。
- `sync-skills.py --check` PASS；`trellium.py check` PASS（0 errors / 0 warnings）；`status` PASS；`git diff --check` PASS。最终 task gates 已据本轮裁决回写；再次 check/status/diff 检查均 PASS，status 确认 implementation/regression partial、review blocked，lifecycle 仍 ready_for_review。证据文件 syntax/whitespace/末尾换行/本地链接检查及双语 bundled source byte-identical 核验 PASS。
- 复核只新增验收 fixture/证据、更新 review/TASK/runtime 元数据；未修改产品代码、未访问真实 Store、未 commit/push、未清理 Docker 镜像。

## Round 3 Fresh Verification · 2026-10-01（PI fix batch 2）

- macOS / Python 3.9.6：全量 256 tests，255 PASS / 1 既有 FAIL（预存 ancestor-swap fixture）；store 20 + identity 17 聚焦 tests 全 PASS。`sync-skills.py --check` PASS（双语内嵌副本 byte-identical）；`check` 0 errors / 0 warnings；`git diff --check` PASS；ruff 对两个分发面产品文件本轮新增行零告警（预存风格项不扩面清扫）。
- Linux / Python 3.12.3 / overlayfs / non-root（本地 `python:3.12.3` 镜像）：store 20/20、identity 17/17、双语分发 importlib E2E（成组 retain→删 clone→找回）PASS；两个 reopened 反例按 reviewer 复现格式独立复跑确认均翻转（见各 finding Verification）。
- 修改面：`scripts/history_store.py`（链延伸 + 构造守卫 + docstring）、`scripts/trellium.py`（`_identity_in_head` 探针）、`scripts/test_history_store.py` +3 测试、`scripts/test_trellium.py` +1 测试并修正一个既有测试前提（操作失败语义需有修订仓库），sync 重新生成派生快照。未 commit/push、未触碰 reviewer 证据文件与 owner 未提交改动；lifecycle 停在 ready_for_review 待重审。

## Round 4 Independent Re-review · 2026-10-01（Codex fix batch 2）

- F29-001 fixed：双平台 20 Store tests PASS，原 bootstrap 反例 `failed parent fsync retried = True`。接受固定同步链与构造时更深缺失祖先的显式 ValueError；守卫有聚焦无写入验证，不扩大 filesystem 保证。
- F29-002 原 loose-ref 反例已翻转为拒绝且无写入，17 identity tests PASS；修正有修订 fixture 的前提符合结构探针语义。但 `scripts/trellium.py:2425–2426` 的非仓库分类仍仅靠 stderr 文本：真实临时仓库提交 identity 后，删 working-tree identity，再将 `.git/HEAD` 改为 `corrupt head\n`，Git 报 `not a git repository`，helper 立即判无绑定，创建并登记不同 UUID。恢复原 HEAD 后原提交 UUID 仍可读取。双平台均复现，F29-002 reopened（P1）。需要对损坏/不可读的既有 Git metadata 返回 unknown，并覆盖无身份/stamp 写入及真实非仓库正例，不新增状态/身份副本/CLI。
- macOS Python 3.9.6：全量 256 tests，255 PASS / 1 预存 ancestor-swap FAIL（14.469 s）；37 聚焦 tests PASS（1.661 s）。Linux Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：37 聚焦 tests PASS（2.590 s）；两平台双语分发 E2E 均 PASS。历史证据不改写，新 fixture/fingerprints/原始输出存入 [batch 2 evidence](../../docs/evals/historical-evidence-store-2026-10-rereview/batch2-RESULTS.md)。
- 本轮仅更新验收记录与证据，未修产品、accepted、commit/push、访问真实 Store 或清理镜像。gates 据唯一剩余 P1 回写 implementation/regression partial、review blocked；lifecycle 保持 ready_for_review。
- 最终回写后 check PASS（0 errors / 0 warnings）、status PASS（确认当前 gates）、diff check PASS；sync in sync、双语产品副本 byte-identical；新增证据的 syntax/whitespace/末尾换行/本地链接检查 PASS。
- Fix (2026-10-01, PI)：非仓库分类不再仅靠 stderr——新增 `_has_git_metadata(target)`（祖先链结构探测，`os.path.lexists` 含 `.git` 目录/指针文件/损坏 symlink；不可读路径 fail closed 为 unknown）；`_identity_in_head` 的 `not a git repository` 分支改为：结构上无任何 `.git` 条目才判可证明非仓库（False），存在 `.git` 条目（含损坏 metadata）返回 unknown 拒绝写入。docstring 同步记录该误导性 stderr 边界。
- Verification：`test_corrupt_git_metadata_fails_closed`（提交身份→删 worktree→改坏 `.git/HEAD`→先钉住 `not a git repository` 确为触发文本→`authorize_create=True` 拒绝且无写入）+ 既有无身份/stamp 与真实非仓库正例保持 PASS；双平台执行。按 reviewer 复现格式独立复跑（Linux 3.12.3 / git 2.39.2）：corrupt `.git/HEAD` → stderr 含 `not a git repository` → `replacement created: False`、无替换文件；恢复原 HEAD 后原 UUID 可读回（证明 metadata 存在、unknown 拒绝是正确处置）；真实非仓库目录（完整 adopt fixture）首次绑定仍可用。

## Round 5 Fresh Verification · 2026-10-01（PI fix batch 3）

- macOS / Python 3.9.6：全量 257 tests，256 PASS / 1 预存 ancestor-swap FAIL；store 20 + identity 18 聚焦 tests 全 PASS。`sync-skills.py --check` PASS（双语内嵌副本 byte-identical）；`check` 0 errors / 0 warnings；`git diff --check` PASS；ruff/lens 对本轮新增行零告警（预存风格项不扩面清扫）。
- Linux / Python 3.12.3 / git 2.39.2 / overlayfs / non-root：store 20/20、identity 18/18、双语分发 E2E（含 bootstrap `.trellium` 布局）PASS；reviewer corrupt-`.git/HEAD` 反例独立复跑确认翻转（见 F29-002 Verification）。
- 修改面：`scripts/trellium.py`（`_has_git_metadata` + `_identity_in_head` 非仓库分支门控 + docstring）、`scripts/test_trellium.py` +1 测试、sync 重新生成派生快照。未 commit/push、未触碰 reviewer 证据文件（`docs/evals/historical-evidence-store-2026-10-rereview/`）与 owner 未提交改动；lifecycle 停在 ready_for_review 待重审。

## Round 6 Independent Re-review · 2026-10-01（Codex fix batch 3）

- 原 corrupt `.git/HEAD` 反例已翻转为拒绝且无替换文件；正常目录/空仓库首次绑定正例通过；旧 loose-ref/ bootstrap 反例保持修复。38 聚焦 tests 与双语 E2E 双平台 PASS，其他三个 findings 保持关闭。
- F29-002 仍 reopened（P1）：`scripts/trellium.py:2423` 调用 `os.path.lexists`，其内部捕获 `os.lstat` 的 OSError 并返回 False；外层 2428 行的 except 收不到该错误。隔离 fixture 在已经提交原 UUID、损坏 HEAD、删除 worktree identity 的临时项目，只对 `.git` 的 Python lstat 查询注入 PermissionError，其余查询/Git 子进程真实执行。detector 返回 False，helper 创建并登记不同 UUID、stamp bytes 改变；恢复原 HEAD 后原提交身份可读。macOS/Linux 均复现。这是明确查询失败注入，不是特定 ACL 或物理故障实测。
- Required fix：metadata lookup 仅在明确不存在时继续祖先探测；权限/IO 等查询失败必须 unknown 且不写 identity/stamp。使用能保留错误类型的 lstat 分类，保留 `.git` directory/gitfile/broken symlink 存在语义和真实非仓库正例；补此错误注入测试。不扩面修 private_preflight，不新增 schema/依赖/CLI。
- macOS Python 3.9.6：全量 257 tests，256 PASS / 1 预存 ancestor-swap FAIL（14.728 s）；38 聚焦 tests PASS（1.781 s）。Linux Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：38 聚焦 tests PASS（2.651 s），双语 E2E PASS。原始 Linux 输出、源码 fingerprints 和 fixture 见 batch 3 evidence；历史证据不覆盖。
- 本轮仅新增验收证据、更新 TASK/台账；未修改产品、accepted、commit/push、真实 Store 或 Docker 镜像。implementation/regression 回写 partial，review blocked，lifecycle 保持 ready_for_review。
- 最终 check PASS（0 errors / 0 warnings）、status PASS（确认当前 gates）、diff check PASS；sync in sync、bundled modules byte-identical、源码 fingerprints current；证据 syntax/whitespace/末尾换行/本地链接检查 PASS。
- Fix (2026-10-01, PI)：`os.path.lexists` 删除（其内部吞 OSError 返回 False，无法区分查询失败与不存在）；改为 `_proven_without_git_metadata(target)` 直接用 `os.lstat` 分类：查询成功 → `.git` 条目存在（False，返回未知路径拒绝）；`FileNotFoundError` → 本层确证不存在，继续祖先探测；其它 `OSError`（含 PermissionError/ENOTDIR/ELOOP）与 `resolve()` 失败 → None（unknown）。仅当全部祖先均确证无条目才返回 True；调用方仅 True 读作可证明非仓库，其余一律 unknown 拒绝。docstring 同步。
- Verification：`test_unqueryable_git_metadata_fails_closed`（真实 adopted fixture：非仓库 stderr 注入 + `.git` lstat PermissionError 注入 → 拒绝且身份文件与 stamp bytes 均未变）+ 既有 corrupt-`.git/HEAD`（entry 存在语义）与真实非仓库/零修订正例保持 PASS；双平台执行。按 reviewer 注入格式独立复跑（Linux 3.12.3 / git 2.39.2）：lstat PermissionError → `replacement created: False`、无身份文件；`/tmp`（确证无 `.git`）→ True、含 `.git` 的仓库目录 → 条目存在语义正确。

## Round 7 Fresh Verification · 2026-10-01（PI fix batch 4）

- macOS / Python 3.9.6：全量 258 tests，257 PASS / 1 预存 ancestor-swap FAIL；store 20 + identity 19 聚焦 tests 全 PASS。`sync-skills.py --check` PASS（双语内嵌副本 byte-identical）；`check` 0 errors / 0 warnings；`git diff --check` PASS；本轮新增代码 lens/ruff 零告警（预存 storage 检查风格项不扩面）。
- Linux / Python 3.12.3 / git 2.39.2 / overlayfs / non-root：store 20/20、identity 19/19、双语分发 E2E PASS；reviewer lstat 注入反例独立复跑确认翻转（见 F29-002 Verification）。
- 修改面：`scripts/trellium.py`（`_proven_without_git_metadata` lstat 三态分类 + 调用方门控 + docstring）、`scripts/test_trellium.py` +1 测试、sync 重新生成派生快照。未 commit/push、未触碰 reviewer 证据文件与 owner 未提交改动；lifecycle 停在 ready_for_review 待重审。

## Round 8 Independent Re-review · 2026-10-01（Codex fix batch 4）

- **APPROVE**，F29-002 fixed：确认 lstat 的三态语义及调用方只有 True 视作可证明非仓库。原错误注入复核输出 `detector = None ; replacement created = False ; identity exists = False ; stamp unchanged = True`；损坏 HEAD/loose ref 均拒绝，恢复 HEAD 可读取原 UUID。目录/gitfile/broken symlink/明确不存在/PermissionError/NotADirectoryError/一般 OSError/resolve OSError 的独立分类 fixture PASS；真实非仓库与零修订正例保持通过。
- 原 F29-001 bootstrap 失败重试仍补同步，其他已关闭 findings 不回退。macOS Python 3.9.6：39 聚焦 tests PASS（1.765 s），全量 258 tests 为 257 PASS / 1 预存 ancestor-swap FAIL（15.201 s）；Linux Python 3.12.3 / Git 2.39.2 / overlayfs / uid 65534：39 聚焦 tests PASS（2.597 s）。两平台双语分发 E2E PASS。完整 Linux 输出、原始观察、源码 fingerprints 和最终规模测量见 batch 4 evidence；历史证据原内容保留。
- 本轮仅新增验收证据与更新 TASK/台账；review 回写 passed，implementation/regression/distribution_sync passed，lifecycle 保持 ready_for_review。范围内 regression 已通过，预存全量失败仍如实披露为 residual；不自动 accepted、commit/push、访问真实 Store 或清理镜像。
- 最终回写后 check PASS（0 errors / 0 warnings）、status PASS（各 gates passed，ready_for_review）、diff check PASS；bundled modules byte-identical、源码 fingerprints current、证据 syntax/whitespace/末尾换行/本地链接检查 PASS。确认 AC 唯一未勾选项为 Owner 接受交付。

## Existing Residuals / Owner Acceptance

- 原 loop F001/F002 按 owner 提供摘要保留为 P3 residual，不把它们升级为本轮 blocker；七项 taste 风险未取得原 verdict 正文，不伪造细节或处置。
- F29-001/F29-002/F29-003 fixed、F29-004 resolved；无剩余独立验收 blocker。Owner 于 2026-10-01 明确确认“验收通过是吧，那我这也通过”，已勾选最后一项 AC，TASK accepted、gates 全部 passed。原 P3 与预存 macOS 全量失败保持披露；原始 ledger/各轮证据保留，不提交或推送。
