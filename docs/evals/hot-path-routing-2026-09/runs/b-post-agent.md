TASK-0100 已完成并落在最终状态。以下按要求给出三项内容。

## (a) 实际读取的文件清单与原因

| 文件 | 原因 |
|---|---|
| `AGENTS.md` | 任务指定的入口规则（必读清单、Forbidden、工作流） |
| `vault/index.md` | 入口必读 1：任务等级与授权速查表、`trellium-policy`（`task_storage: tracked`） |
| `vault/runtime.md` | 入口必读 2：全局状态、Required Checks、Focus（TASK-0028，仅导航） |
| `vault/governance.md` | Level B 判定模糊时追加必读：任务分级、Authority 1–4、验收门、escalation、handoff 双重触发 |
| `vault/project.md` | 首次进入项目必读：目标/边界（“保留既有行为、高影响需批准”） |
| `vault/handoff.md` | 接手真实中断任务必读：TASK-0100 的 transient delta 与 Exact resume point |
| `vault/tasks/TASK-0100-install-dry-run.md` | 追踪任务文件：状态块（Level B / Authority 2 / gates）、Objective、Scope、AC、Forbidden |
| `vault/tasks/README.md` | 状态块唯一 owner 规则、任务契约必需段落、Execution Record/Memory Updates 模板 |
| `install.sh`（仓库根，未跟踪） | 现场调查：handoff 所说的 `print_plan` stub 实际落在此杂散文件（被 .gitignore 忽略） |
| `scripts/install.sh` | 真正的被改源码（README/CI 引用的即此文件），实现 `--dry-run` 的目标 |
| `scripts/test_install_sh.py` | 聚焦测试目标文件（“聚焦测试覆盖两个分支”AC） |
| `docs/engineering/profiles/python-backend.md` | 改动含 Python 测试，按 AGENTS 路由读取实际语言的 profile；仓库无 shell profile，故 `install.sh` 按仓库既有 sh 风格（`set -eu`、POSIX） |
| `docs/engineering/code-comments.md` | 行为与注释同改，按 AGENTS 与 profile 并读（注释表达以它为准） |
| `README.md` / `README.en.md`（grep 定位） | 确认 `install.sh` 的规范引用是 `scripts/install.sh`（L158），排除根目录杂散文件 |
| `RUNLOG.md` | 规则 4 要求的命令日志（本次创建并逐行追加） |

## (b) 任务分级与授权判断

- **分级：Level B（已由任务文件状态块确认 `level: "B"`）**。依据 `vault/index.md` 速查表与 `vault/governance.md` 判定顺序：不命中 Level C 风险域——不改安全/隐私、不改持久数据/迁移、不改部署、不改依赖、不改成本配额、不改架构方向、不改治理规则；也不改网络协议与默认安装行为（均在 Out of scope/Requires approval，我未触碰）。命中 Level B 条件：真实 handoff（跨 session 中断）、多阶段 gate（plan/implementation/tests）、需追踪验收。规模（2 个代码文件）只作提示，不单独决定等级。
- **授权等级：2（限定范围修改）**，依据状态块 `authority_level: 2` 与 Authority 正文：Allowed = “修改 `install.sh` 及其聚焦测试”。`--dry-run` 是任务自身显式授权的 opt-in 新行为（若视为需批准的公开契约改动，任务契约不会把它列为 Allowed）；我未触碰 Requires approval 项（默认安装行为、网络路径）与 Forbidden 项（`--version` fail-closed 语义保留、既有输出契约未改——dry-run 只是新增 opt-in 输出）。
- **是否请求/需要授权：未请求，也不需要。** Authority 2 在边界与检查内覆盖本次改动；无范围扩大、无检查失败、无用户改动冲突，故未触发 escalation（`contact_supervisor` 未使用）。Level B 的任务文件更新、runtime 单行投影、handoff delta 消费均属治理要求的常规动作。

## (c) 变更摘要与验证结果

**现场还原**：工作树在 `d477a79`（fixture overlay，相对基线 `77ee022` 的 7 文件改动即“已有改动”：TASK-0100 文件、handoff 条目、runtime/index、docs profiles）；代码侧此前仅剩 handoff 描述的半成品——`print_plan()` stub 落在**被忽略的根目录杂散 `install.sh`**，而 tracked 的 `scripts/install.sh` 完全没有 dry-run，测试文件未动。

**变更**（5 个已跟踪文件，+211/−68，均未 staged）：
1. `scripts/install.sh`：新增 `--dry-run` 解析与 `print_plan()`；把输入解析/校验（`--source` 校验、`--version` fail-closed）整体移到 `mktemp`/`curl`/`tar`/安装等任何副作用之前，dry-run 在此打印计划后 `exit 0`；抽取 `resolve_destinations()` 供计划与真实安装共用（单一事实来源，避免漂移）；usage/头部注释同步。正常执行路径语义与输出保持不变。
2. `scripts/test_install_sh.py`：新增 3 项聚焦测试（source dry-run 计划+零写入；network dry-run 缺 `--version` 仍 fail-closed 且零网络；network dry-run 带 `--version` 打印计划且零网络零写入），fake curl 抽为 `make_fake_curl`/`run_network_installer` helper 并被既有测试复用；正常执行分支由既有 7 项测试覆盖 → 两个分支均有覆盖。
3. `vault/tasks/TASK-0100-install-dry-run.md`：状态块 → `ready_for_review` / `complete` / gates 全 passed；3 条 AC 勾选；补齐契约缺失段落（Context Required、Capability Tags、Verification、Execution Record、Memory Updates，disposition = `not_applicable` — tracked）。
4. `vault/runtime.md`：Current Progress 增加 1 行投影。
5. `vault/handoff.md`：TASK-0100 条目按规则“消费后即删”移除。
另创建 `RUNLOG.md`（被 `.gitignore` 的 `/*` 忽略，不进版本控制），逐条记录命令+原因。

**验证（均为本机实跑）**：

| 命令 | 结果 |
|---|---|
| `sh -n scripts/install.sh` | SYNTAX_OK（`/bin/sh` = dash） |
| `python3 -m unittest scripts.test_install_sh -v` | 10/10 OK（含 3 项新测试） |
| `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` | **216/216 OK**（基线 213 + 3） |
| `python3 scripts/sync-skills.py --check` | in sync（两包） |
| `python3 scripts/trellium.py status . --format json` | findings `[]`；TASK-0100 `ready_for_review`、gates 全 passed |
| `python3 scripts/trellium.py check . --format json` | errors 0 / warnings 0 |
| `git diff --check` | clean |
| `git diff --cached --name-only` / `git status --porcelain -uall` | 无 staged 文件；仅 5 个已跟踪修改 |
| 手工 dash 演示：`--source . --dir … --dry-run` | exit 0，输出 `plan: source …` + `plan: install trellium -> …/demo-target/trellium`，目标目录未创建 |
| 手工：`sh scripts/install.sh --dry-run`（网络、缺 version） | exit 1，fail-closed 报错原文不变，无 plan 输出 |
| 本地 fake curl + 本地 tarball 端到端跑网络分支 | exit 0，`==> fetching`→`==> installed`→Next 提示，**未访问真实网络**；临时目录已清理 |

未执行任何 `git add/commit`，未调用任何真实外部系统（网络分支仅用本地 fake curl/tarball 验证），所有读写均在 `/tmp/trellium-0028-fx2/b-post` 内（测试套件自建/自清的系统临时目录除外）。

**开放风险**：① 仓库根残留被忽略的杂散 `install.sh`（仅 `print_plan` stub），未删除（不静默覆盖先前改动），是否清理待 owner 决定；② 真实 GitHub tarball 下载未实测（禁用真实外部系统），仅以 fake curl 验证了搬移后的 fetch 代码路径；③ dry-run 在 agent 检测失败时与真实运行一致 exit 1 且不输出计划（已在任务文件 Risks 记录）。