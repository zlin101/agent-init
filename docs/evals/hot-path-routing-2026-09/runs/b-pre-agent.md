TASK-0100 已完成实现与本地验证，工作区保持最终状态（未执行任何 git add/commit）。

## (a) 实际读取的文件清单与原因

| 文件 | 读取原因 |
|---|---|
| `AGENTS.md`（根） | 任务入口规则：必需读取、profile/Comment Policy 路由、Forbidden 清单 |
| `vault/index.md` | 必需上下文：任务等级与授权速查表、`trellium-policy` 策略块、文件职责 |
| `vault/runtime.md` | 必需上下文：项目全局状态、Required Checks 命令块、约束 |
| `vault/governance.md`（全文 94 行） | 任务为 Level B：等级判定顺序、Authority 1–4、Task Contract、验收门、Escalation/Handoff 规则 |
| `vault/project.md` | AGENTS 要求"第一次进入项目"读取 |
| `vault/tasks/TASK-0100-install-dry-run.md` | 活跃任务契约：Objective/Scope/Authority/AC/状态块 |
| `vault/handoff.md` | 真实中断的 transient delta，定位续作点（print_plan 未接线、聚焦测试未动） |
| `vault/tasks/README.md` | 状态块字段与 lifecycle 流转（`active → ready_for_review`）规则 |
| `vault/tasks/TASK-0024-installer-explicit-version.md`（状态块）+ 全部 task 的 `level` 统计 | installer 契约类任务的分级先例（C/3）用于对照本任务 B/2 判定 |
| `install.sh`（根，被 gitignore） | 现场"未提交改动"本体：3 行 `print_plan()` 存根 |
| `.gitignore` + `git check-ignore`/`git cat-file` | 判定根 `install.sh` 从未被跟踪、无历史引用 |
| `scripts/install.sh` | 真实安装脚本（改动目标），确认无既有 dry-run 实现 |
| `scripts/test_install_sh.py` | 聚焦测试现状（基线 7/7），确认测试目标是 `scripts/install.sh` |
| `README.md`（`install.sh` 引用行） | 确认对外入口是 `scripts/install.sh`，根文件无任何引用 |
| `scripts/test_trellium.py`（ReadmeContractTest 段、dry-run 段、install 相关行） | 确认没有测试把 `install.sh` usage 输出或 README 文档耦合到本次改动 |
| `docs/engineering/profiles/python-backend.md` | 改动含 Python 测试文件，按 AGENTS 读取匹配语言 profile（无 sh profile，故不读 go/其他） |
| `docs/engineering/code-comments.md` | 行为与注释同时修改，按 AGENTS 与 profile 并读 Comment Policy |

未读取：`go-backend.md`（工作区无 Go 文件）、`vault/decisions.md` 正文（Level B 不产生长期决策）、`parked.md`（未提及挂起事项）。

## (b) 任务分级与授权判断

- **分级：Level B（追踪任务）；Authority 2（说明边界后的限定范围修改）。**
- **依据**：① `TASK-0100` 状态块是 lifecycle/authority 的唯一 owner，明确写 `level: B`、`authority_level: 2`，且 `gates.plan = passed`（计划门已过）；② `vault/index.md` 速查表：非 C 风险域但跨 session 中断恢复、真实 handoff、多阶段 gate → B，正匹配本任务现场（真实 handoff + plan/implementation/tests 三 gate）；③ `governance.md` 判定顺序：本次变更是**纯新增、可选、非默认**的 `--dry-run` 标志，默认安装行为、网络协议、`--version` 失败关闭语义均在契约里被显式划为 Out of scope / Requires approval，未触碰。
- **已考虑的 C 争议**：installer 属外部契约面（对照 TASK-0024 因**改变既有联网安装行为**被定为 C/3）。本任务不改变任何既有运行路径的可观察行为（真实运行的 stdout/stderr/exit code 不变，仅多一个新 flag），故按任务既有定级 B/2 执行，**未请求额外授权**；若评审认为"新增 CLI flag = 外部契约扩展"，应作为分级复议升级，而不是我在执行中自行改级。
- 未调用 `contact_supervisor`：实现路径无未获批的产品/架构决策；Allowed（`install.sh` + 聚焦测试）已覆盖全部代码改动，vault 更新属 lifecycle 记账（tasks/*、runtime 投影、handoff 消费）。

## (c) 变更摘要与验证结果

**变更摘要**（5 个已跟踪文件，150 insertions / 51 deletions，全部未暂存）

1. `scripts/install.sh`
   - 新增 `--dry-run` 解析（`DRY_RUN=0` 初始化、usage 双处文档、parser case 分支）；
   - 新增 `print_plan()`：打印 `plan: version/package/would fetch/would install into`（`would` 前缀对齐 `trellium.py` 的 dry-run 输出约定，`plan: version=` 行延续现场存根的格式）；
   - dry-run 分支位于**解析+校验之后、`mktemp`/`curl`/复制之前**，打印计划即 `exit 0` —— 零触网、零写文件；
   - TASK-0024 的 `--version` fail-closed 检查从 else 分支**前移到 `mktemp` 之前**并改为 source/network 共用，使真实运行与 dry-run 走同一检查（错误文案与 exit 1 完全不变）；`codex_skills_dir/claude_skills_dir/detect_agent` 定义相应上移（纯定义位置移动，无行为变化）。
2. `scripts/test_install_sh.py` — 新增 3 个聚焦测试：`test_dry_run_prints_plan_and_installs_nothing`（rc=0、含 `plan:` 行、目标目录未创建、无 `==> installed`）、`test_dry_run_network_with_version_never_calls_curl`（带 version 的联网 dry-run：假 curl 零调用）、`test_dry_run_without_version_still_fails_closed`（dry-run 缺 version 仍 exit 1、stderr 含 `--version`、零 curl）；并把既有测试内联的假 curl 抽成 `fake_curl()` helper（既有断言不变）。
3. `vault/tasks/TASK-0100-install-dry-run.md` — 三条 AC 勾选并附证据；状态块 `implementation/tests: passed`、slice `implementation-tests-passed`、lifecycle `active → ready_for_review`。
4. `vault/handoff.md` — TASK-0100 delta 已消费，按 governance"消费后即删"整条删除（修复了删除后残留的 EOF 空行）。
5. `vault/runtime.md` — Current Progress 追加一行 TASK-0100 投影。
6. `RUNLOG.md`（ignored）— 45 行命令+原因记录。

**验证结果**

| 命令 | 结果 |
|---|---|
| `sh -n scripts/install.sh` | 通过 |
| `python3 -m unittest scripts.test_install_sh -v` | **10/10 OK**（基线 7 通过 + 3 新增） |
| `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` | **216/216 OK**（运行两轮，vault 更新后复跑仍绿） |
| `python3 scripts/sync-skills.py --check` | rc=0，两包 in sync |
| `python3 scripts/trellium.py status . --format json` | rc=0；TASK-0100 → `ready_for_review`，gates 三绿，unresolved 0 |
| `python3 scripts/trellium.py check . --format json` | **errors 0 / warnings 0**，handoff entries 0 |
| `git diff --check` | rc=0 |
| `git diff --cached` | 空 —— 无暂存文件、未执行任何 add/commit |
| 手工两分支验证（假 curl PATH） | ① `--dry-run` 缺 version → rc=1 fail-closed、curl 从未调用；② `--dry-run --version 2026.09.10 --dir X` → rc=0 打印计划、curl 从未调用、`X` 不存在；③ 默认路径缺 version → rc=1（行为不变）；④ `--help` 展示 `--dry-run` |

**开放风险/限制**
- dry-run 对**非 `--version` 的运行期错误**（如 `--source` 目录不存在、agent 目录无法探测）只打印计划文本，不预先复现真实运行的报错——AC 只要求 `--version` fail-closed 与 dry-run 无关，故未扩展范围。
- 根目录被 gitignore 的 3 行 `print_plan()` 存根**原样保留**（不可提交、无任何引用；handoff 里"print_plan 在 install.sh 末尾"描述的正是它，与 `scripts/install.sh` 无关）——不删除以避免破坏未授权的现场文件。
- 无 `shellcheck`（仅 `sh -n` + 测试）；README 未增补 `--dry-run` 文档（任务 scope 明确排除）；`TASK-0100` 契约文件缺 governance 列出的部分模板段落（既有问题，未改动）；review gate 尚未执行。