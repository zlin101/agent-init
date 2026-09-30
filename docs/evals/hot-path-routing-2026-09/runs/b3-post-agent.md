TASK-0100 已完成实现并验证，工作区保持最终状态（未 add、未 commit）。

## (a) 实际读取的文件清单与原因

| 文件 | 原因 |
|---|---|
| `AGENTS.md`（工作区） | 任务规则要求按其入口规则开始工作 |
| `vault/index.md` | AGENTS.md 必读 ①：任务等级/授权速查表、策略块 |
| `vault/runtime.md` | AGENTS.md 必读 ②：项目全局状态、必检清单、约束 |
| `vault/project.md` | AGENTS.md「第一次进入项目」必读 |
| `vault/handoff.md` | 真实中断任务（TASK-0100 续作）必读；取回 resume point |
| `vault/governance.md`（全文 94 行） | Level B 任务 → AGENTS.md 要求追加读取；取等级/授权/验收门/升级规则 |
| `vault/tasks/TASK-0100-install-dry-run.md` | 追踪任务必读；任务契约、Scope、Authority、AC、状态块 |
| `vault/tasks/README.md` | 状态块字段、lifecycle 流转、Execution Record 模板 |
| `scripts/install.sh` | 修改目标；定位 `--dry-run` 接线点与 TASK-0024 版本门 |
| `scripts/test_install_sh.py` | 聚焦测试目标文件（现有 7 个用例与 fake curl 模式） |
| `.gitignore` | 判定根 `install.sh`/`RUNLOG.md` 为何被忽略（`/*` 白名单式） |
| `docs/engineering/profiles/`（仅列目录） | 查 root 匹配 profile；只有 go/python 两种语言，与 shell 不匹配 → 按 AGENTS.md 不读未匹配语言 |
| `scripts/trellium.py`（片段 1583–1745、1600 行） | 确认 `trellium-task-state` 必填字段与 `GATE_VALUES` 合法取值，避免改坏 `check` |
| `vault/index.md`/`runtime.md` 的 overlay diff | 弄清「现场」：fixture overlay 提交 `a5c1ade` 做了什么 |
| `RUNLOG.md`（自检） | 复核命令日志完整性 |

未读：`docs/engineering/code-comments.md`（非纯注释工作）、`docs/engineering/profiles/*` 正文（无 shell 匹配 profile）、`vault/parked.md`（未提及挂起事项）、`vault/handoff.md` 之外的其他任务文件（只处理 TASK-0100）。

**现场还原**：工作树相对 `77ee022` 的"部分改动"由 fixture overlay 提交 `a5c1ade` 承载（TASK-0100 任务文件、TASK-0100 handoff 条目、runtime/index 改动）；另有根目录 4 行 `install.sh` 残片（只含 `print_plan()`，被 `.gitignore` 的 `/*` 忽略、历史上从未被跟踪）。真正的安装脚本是 `scripts/install.sh`（README 的 curl URL、`scripts/test_install_sh.py`、TASK-0024 历史都指向它），handoff 所述"print_plan 已定义但未接线"在该文件中并不存在 → 判定根残片是上一会话的搁浅草稿，接线目标为 `scripts/install.sh`。

## (b) 任务分级与授权判断

- **Level B（追踪任务），Authority 2（限定范围）** ——依据：任务文件状态块显式声明 `"level": "B"`, `"authority_level": 2`；按 `vault/index.md` 速查表与 `governance.md` 判定顺序，本任务不命中 Level C 风险域（未改安全/隐私、公开 API/外部契约、持久数据、依赖、成本配额、架构方向、治理规则），但属于跨 session、有真实 handoff、多阶段 gate 的追踪任务。分级为最初判定，中断不追溯改写。
- **授权**：任务正文 Allowed =「修改 `install.sh` 及其聚焦测试」，本次改动（`scripts/install.sh` + `scripts/test_install_sh.py` + 任务文件/runtime/handoff 记录）全部落在该边界内；`Requires approval`（改变默认安装行为或网络路径）与 `Forbidden`（移除 `--version` 失败关闭语义、未确认改变输出契约）均未触及——默认安装路径、网络协议与错误文案保持原样，仅新增 `--dry-run` 只读输出。**因此未请求额外授权**（Authority 2 无需升级到 3）。未执行 git add/commit，未访问任何外部业务系统，未运行破坏性命令。
- 曾评估的判断点（目标文件歧义）证据充分，自行判定并已在任务 Execution Record 与本报告中留痕，无需升级。

## (c) 变更摘要与验证结果

**变更（5 个跟踪文件，+197/−42）**
1. `scripts/install.sh`（+50/−8）：usage 头与 `usage()` 增加 `[--dry-run]`；`DRY_RUN=0` 与 `--dry-run) DRY_RUN=1; shift ;;` 复用既有 flag 解析（未知参数仍在任何网络/副作用前以 2 拒绝）；把 TASK-0024「缺 `--version` fail-closed」门从 `mktemp` 之后提到之前（条件等价，错误文案不变），保证 dry-run 无法绕过；新增 `print_plan()`（lang/package/source/tag/target/action/side-effects 七行计划），在解析与校验之后、`mktemp`/`curl`/`cp` 之前打印并 `exit 0`。
2. `scripts/test_install_sh.py`（+91/−22）：抽 `recording_curl_environment()` helper（原网络测试改为复用，语义不变）；新增 3 个聚焦测试：`test_dry_run_flag_toggles_plan_vs_install`（dry-run 只出计划且目标目录不存在 / 同命令去掉 flag 正常安装 → 覆盖两个分支）、`test_dry_run_network_plan_never_touches_network`（有 `--version` 的网络计划：rc=0 且记录型 curl 零调用、零写入）、`test_dry_run_still_fails_closed_without_version`（dry-run 缺版本仍 rc=1、curl 零调用）。
3. `vault/tasks/TASK-0100-install-dry-run.md`：状态块 `lifecycle=ready_for_review`、`current_slice=implementation-verified`、`gates` 三项全 `passed`；AC 三项勾选；补齐契约章节（Context Required/Capability Tags/Verification/Execution Record/Memory Updates）。
4. `vault/runtime.md`：Current Progress 增加一行 TASK-0100 投影（Focus 仍为 TASK-0028，未改动）。
5. `vault/handoff.md`：删除已消费的 `## TASK-0100` transient delta（governance 要求消费后即删）。
6. `RUNLOG.md`（被 gitignore，任务契约要求）：33 行，每条命令附一句原因。

**验证（基线先跑，改动后复跑）**

| 命令 | 结果 |
|---|---|
| `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` | 基线 213 OK → **改动后 216 OK**（+3 新测试） |
| `python3 -m unittest scripts.test_install_sh -v` | 10/10 OK |
| `sh -n scripts/install.sh` | syntax OK |
| `python3 scripts/sync-skills.py --check` | rc=0，两处 in sync |
| `python3 scripts/trellium.py status . --format json` | rc=0，findings=[]，TASK-0100=`ready_for_review` 且 gates 全 passed |
| `python3 scripts/trellium.py check . --format json` | rc=0，**errors 0 / warnings 0** |
| `git diff --check` | rc=0 |
| 人工冒烟 | dry-run 计划 rc=0 且 `/tmp/x` 未创建；缺版本 dry-run rc=1；`--dry-run --bogus` rc=2；source 模式计划 rc=0 |

**遗留风险**：① 根目录被忽略的 4 行 `install.sh` 残片未删除/未改动（超出 Allowed 范围，属"不静默覆盖改动"，留给 owner 决定）；② 计划输出对默认目标只打印 `target=auto-detect (codex|claude)`，不提前做只读探测（记录在任务 Risks）；③ README 未加 `--dry-run` 示例（docs 不在 Scope 内）；④ runtime Focus 指向的 TASK-0028 在本工作区无任务文件（`resolved: false`，先于本次改动即存在，与本任务无关）；⑤ 未 push、未 release、未 commit。