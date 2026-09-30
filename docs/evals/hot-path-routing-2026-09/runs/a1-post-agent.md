任务已在 `/tmp/trellium-0028-fx2/a1-post` 内完成。以下按要求给出三部分说明，并附验收报告。

## (a) 实际读取的文件清单与原因

| 文件 | 读取原因 |
|---|---|
| `AGENTS.md` | 任务入口规则要求首读，确定必读清单、工作原则与禁止项 |
| `vault/index.md` | 入口规则必读；取「任务等级与授权速查表」与 `trellium-policy` 策略块 |
| `vault/runtime.md` | 入口规则必读；取当前状态与 **Required Checks（仓库验证入口）** |
| `vault/project.md` | 入口规则要求「第一次进入项目时」读取 |
| `vault/governance.md` | 分级判定初期存在模糊（版本字符串是否触及「公开 API」风险域），按 `index.md`「判定模糊→读完整 governance」执行 |
| `docs/engineering/profiles/go-backend.md` | 需修改 Go 源码，按入口规则读取当前路径/语言匹配的 profile |
| `README.md` | 任务目标文件，定位拼写错误（H1 `# Trelium`） |
| `internal/httpapi/router.go` | 任务目标文件，定位版本字符串拼写错误（`"verison "`） |
| `scripts/test_trellium.py`（2900–2960 行） | 检查 `ReadmeContractTest` 是否对 README 改动有测试约束，避免破坏验收门 |
| `README.en.md`（`head`，命令读取） | 对照英文版 H1 `# Trellium`，确认正确拼写基准 |
| `.github/workflows/skill-sync.yml`（命令读取） | 确认 CI 的实际验证入口（unittest + check + sync --check），与 runtime.md Required Checks 交叉验证 |
| `.gitignore` + Git 元数据（命令读取） | 确认 `internal/`、`RUNLOG.md` 的跟踪/忽略状态，解释 `git diff` 为何不显示 router.go |
| `RUNLOG.md`（命令读取） | 复核每条命令均已追加日志 |

未读取 `docs/engineering/code-comments.md`（Comment Policy）：本次改动是字符串字面量与 README 标题拼写，不涉及注释/Doc Comment/TODO/directive 表达，Comment Policy 不适用——此为有意判断，非遗漏。

## (b) 任务分级与授权判断

**分级：Level A（简单任务）；授权等级：Authority 1（低风险局部修改）。**

依据（`vault/governance.md` 判定顺序）：
- **非 Level C**：逐项核对风险域均未命中——非安全/隐私、非持久数据/迁移、非部署、非依赖、非成本/配额、非架构方向、非治理规则。唯一曾存疑的是「公开 API/外部契约」域（HTTP handler 返回的版本字符串），但核实后不构成公开契约：仓库根无 `go.mod`、无 server 装配、`internal/` 被 `.gitignore` 的 `/*` 规则整体忽略（未跟踪），该字符串无任何已发布消费方；全仓 grep 确认 `verison` 无其他引用依赖。
- **非 Level B**：单文件各一行的 diff、验证可低成本重跑，无跨 session handoff、多 owner 或多阶段 gate。
- **→ Level A**：低风险，工作区 + diff + 测试足以恢复。

**是否请求授权：未请求，也不需要。** 固定任务本身即明确指令（修复两处指定拼写 + 运行验证入口），构成 Authority 1 范围内的直接授权；未触及任何需要确认的高影响域。Level A 按规则**不创建/更新 TASK 文件**；project-global runtime 未发生变化（拼写修复不改变阶段/进度），故不更新 `vault/runtime.md`。全程未执行 `git add/commit`，未调用任何外部业务系统（也未触发包注册表安装）。

## (c) 变更摘要与验证结果

**变更（2 个文件，各 1 行）：**
1. `README.md:1`：`# Trelium` → `# Trellium`（fixture overlay `b007df7` 植入的错误）
2. `internal/httpapi/router.go:9`：`w.Write([]byte("verison " + version))` → `"version " + version`
3. `RUNLOG.md`：按规则逐行追加了全部命令与读取记录（35+ 行，被 gitignore，属任务要求产物）

**验证（仓库验证入口 = `vault/runtime.md` Required Checks，与 CI 一致）：**

| 命令 | 结果 |
|---|---|
| `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` | **passed** — Ran 213 tests, OK |
| `python3 scripts/sync-skills.py --check` | **passed** — in sync（两个 Skill 快照均无漂移） |
| `python3 scripts/trellium.py status . --format json` | **passed** — exit 0，findings 空 |
| `python3 scripts/trellium.py check . --format json` | **passed** — exit 0，errors 0 / warnings 0 |
| `git diff --check` | **passed** — 无空白错误 |
| `gofmt -l -e internal/httpapi/router.go`（go-backend profile 要求） | **passed** — 无输出，格式与语法正常 |
| `grep -rn 'Trelium\|verison' README.md internal/` | exit 1 — 两处拼写错误零残留 |
| `git diff --cached --stat` | 空 — **无暂存文件** |

**遗留说明（非本任务范围）：** README「本地验证」段写的 `uv run pytest` 在本 fixture 已失效（无 `pyproject.toml`/`tests/`），且未运行它——`uv run` 会写入工作目录之外的 `~/.cache`，与规则 1 冲突；实际验证入口以 runtime.md Required Checks 为准，已全部执行。另因 `internal/` 被忽略，router.go 不受 `git diff`/`git diff --check` 覆盖，改以 `gofmt -e` + 文件内容复核取证。