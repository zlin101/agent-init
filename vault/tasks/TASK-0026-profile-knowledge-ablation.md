# TASK-0026 - Profile knowledge ablation (Round 2)

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0026",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted",
  "current_slice": "accepted-profile-knowledge-ablation",
  "gates": {
    "plan": "passed",
    "implementation": "passed",
    "behavioral_replay": "passed",
    "distribution_sync": "passed",
    "review": "passed"
  }
}
-->

## Objective

将 Go/Python Profile 从包含教程的工程手册收敛为高信息增益的工程 fallback policy：删除教学载荷与重复正文，保留会影响实现决策的偏好和风险约束。只做 advice-form-GPT.md 的 Round 2，不同时改变读取路径。

Decision 是当时判断的留痕，不是不可推翻的法律。D-0011 提供旧方案的背景和失败模式，不拥有否决本轮消融的权力；新证据可以修正原方案，不需要先做 Decision → Rationale 迁移。依据和变化留痕即可，不为了维护旧文本保留冗余。

## Ownership

- Codex 本轮只交付计划，不修改 Profile；PI 接手后实施 M0–M3。
- PI 停在 `ready_for_review`；Codex 独立验收，owner 决定 accepted。
- 不自行 stage、commit、push、tag 或发布。
- 2026-09-30 owner 在 Codex APPROVE 后明确确认 accepted 并授权本地提交；本次不授权 push、tag 或发布，并行 TASK-0027 与讨论文件不纳入提交。

## Scope

### In Scope

- `init/protocol/profiles/go-backend.md`、`python-backend.md`：内容消融。
- `skills/trellium/assets/templates/docs/engineering/profiles/*.md`：英文等价消融。
- 运行现有 sync 机制生成中文模板及双语 protocol-source snapshots/manifest，不手改 generated 文件。
- `scripts/test_trellium.py`：仅相关 Profile 内容契约断言与必要回归，不增加测试 subsystem。
- `init/MIGRATIONS.md`：新增 Unreleased 简短说明，记录内容变化与定制保护，不改已发布历史条目。
- 必要时给 D-0011 追加简短复评说明：解释本轮取代的判断及依据，保留历史背景，不新增 decision/rationale 文件。
- 本任务及必要 project-global runtime 更新。分类表、对照结果写在本任务内，不新建报告。

### Out of Scope

- Round 3/4：AGENTS/index/runtime 路由重设计、少读 index、Decision 改名或 schema 迁移。
- Comment Policy 正文/ownership、per-root override、新 profile、自动语言识别。
- 修改 `scripts/trellium.py` 或 sync 实现、CLI、roots、stamp schema、文件布局、merge/overwrite/proposal/storage 语义。
- 修改 installer、H1–H4、Review Ledger、依赖、CI 或现有工程工具配置。
- 拆出主题文档、增加 router/metadata/parser/checker/持久状态、将删除正文搬到另一个必读文件。
- 操作 Orion 或其他仓库，重建本仓 `docs/engineering/`，修改 `vault/.agent-init.json`，发版。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/collaboration.md`。
- `advice-form-GPT.md` Round 2 与反证/停止条件；若该 owner-local 文件不可用，本任务仍是完整执行契约。
- 两份 canonical Profile、双语 Profile 模板、双语 CODE_COMMENTS.template（仅用于核对 owner，不修改）。
- `init/protocol/70-adoption-flow.md`「Profile 工程规范」、D-0011、TASK-0025（读取既有边界，不重开任务）。
- `scripts/test_trellium.py` 的 Profile adoption/upgrade/localization/routing 用例；`scripts/sync-skills.py` 的派生机制。

## Capability Tags

- documentation
- testing
- agent-governance

## Authority

Allowed:

- Owner 将本任务交给 PI 实施后，按 In Scope 做最小 patch；只在本仓或临时 fixture 中验证。
- 删除通用语法示例、重复叙述、命令教程；合并相同约束并修正相关内容断言。
- 使用现有同步及测试，不真实调用业务外部系统，不使用生产凭据。

Requires Approval:

- 改变工程偏好本身，例如移除 uv/FastAPI 默认值、放宽资源/取消/安全约束；本任务不默认授权。
- 超出文件边界、跨仓库操作，以及 accepted/commit/push/tag。

Forbidden:

- 把“模型应该知道”当作已验证证据，或把标题/关键词测试通过当作行为无退化证明。
- 为让测试绿而删除仍有效的安全/升级/定制保护断言；顺手修 lint/import 等存量问题。
- 用更长路由、额外必读文件或新机器状态替代被删正文；预设行数/token 缩减 KPI。

## Execution Plan

### M0 — 冻结基线与删除候选

1. 读取当前 HEAD/worktree，保留他人修改；在 `/tmp` 保存本轮文件基线与 hash，记录真实测试/check 基线。不要从本计划推断全量已通过。
2. 在本任务内按规则组列短表：`原位置 | KEEP/DELETE/REPO-DERIVED/MOVE | 原失败模式 | 删除后防线/证据`。同组归并，独立风险约束不能藏在教程整段删除中。
3. DELETE 是候选判断，不是自动证明；REPO-DERIVED 必须指出事实来源及“来源缺失时”的 fallback。MOVE 只允许合并到现有同职责位置或引用现有 owner，禁止新增载体。
4. 冻结小型本地 before/after 场景与判定标准，再修改正文。无须创建大型 benchmark 或第二份计划。

### M1 — 只削减教学载荷，保留决策约束

| 内容组 | 最小处置 | 不可随正文一起丢掉的内容 |
|---|---|---|
| Go module 常用命令、基础语法/测试 API 说明 | 删教程或合并为短约束 | module/workspace 运行目录、依赖授权、锁文件/工具链变更审查 |
| 两语言推荐目录树、重复分层介绍 | 删示意骨架，保留真正的边界偏好 | 稳定本地结构优先、不机械创建层/接口、不强推新架构 |
| Python 分页响应、Pydantic 模型、Settings 代码例 | 删示例，保留行为/偏好语义 | 公共契约、配置/密钥边界；API 文档表达仍归 Comment Policy |
| 工具版本、格式/测试入口、目录发现 | 优先合并成 repo-derived 规则 | 有配置时遵从；缺配置时原默认偏好仍有明确 fallback |
| 标准库优先、uv/FastAPI 等工具选择、类型注解 | 保留偏好，去重 | 不借消融更换默认栈或强制既有仓库迁移 |
| 资源、取消、并发、HTTP/API、失败路径 | 保留高信息增益约束 | ownership/停止路径、错误链、输入边界、超时、安全/兼容、验证要求 |

不机械删掉 `%w`/`errors.Is`/`errors.As`、`t.Cleanup` 等字面词：教学解释可删，但若承担错误链、分支或清理约束，应保留一条可执行语义。也不为凑删减量保留/删除整个章节。

### M2 — 分发与回归

1. 英文模板做等价消融；中文由 sync 派生。不只优化中文行数而让英文语义漂移。
2. 更新确实失效的正文/标题断言，继续冻结保留的偏好与风险约束。不得弱化 roots、语言隔离、定制不覆盖、proposal、存储及路径安全测试。
3. 走现有 sync，增加简短 Unreleased 说明。D-0011 若与本轮最终判断冲突，追加复评，不伪改过去为何选择完整 Profile。

### M3 — 反证回放与独立 review 门

同一场景固定 task/repo 输入，仅替换消融前后 Profile；Go/Python 均有覆盖。用本地 fixture 做有限行为回放，记录可检查的结果，不只给自评结论。Agent 工具无法执行时如实标记缺证据，不把行为 gate 填 passed。

| 场景 | 比较什么 | 否决条件 |
|---|---|---|
| 普通低风险修改，repo 已有布局/测试/工具 | 是否沿用本地契约，不加框架/层 | 后版强推默认栈或额外依赖 |
| 新项目或缺工具配置 | 原工程偏好是否仍明确，且只按任务需要初始化 | 以“repo 可推导”为由丢失 fallback |
| 多 module/workspace 或非根目录入口 | 运行目录/受影响范围判断 | 根目录一次测试被误当全覆盖 |
| 并发/异步取消与资源释放 | ownership、停止/清理/错误路径 | 任一保留的风险约束被漏掉或改变 |
| API/输入边界及注释表达 | 行为约束仍在 Profile，表达仍归 Policy | 安全/兼容退化或重复 owner 回归 |
| 已定制 Profile 的真实 upgrade/proposal | 保留本地规则，pristine 正常刷新 | 覆盖定制或输出/升级语义变化 |

反证失败时先撤回该组删除或恢复最短约束，不默认增加系统。恢复必要约束仍算有效消融；无法净减低价值内容，或需要扩展机制才能安全执行，则停止并交 owner。

## Acceptance Criteria

- [x] 分类短表指出删除项原职责和替代防线；没有仅凭“常识”宣称安全。（round-1 已更正 flake8 行与两处事实来源行）
- [x] 教程/示例/重复正文真实减少，没有转移到更多必读文件、长路由或 execution history。
- [x] 原工程偏好、本地契约优先和缺配置 fallback 保留；高风险约束未被整段误删。（含 round-1 补回的 `Application/Use Case → Domain` 依赖方向）
- [x] 文件布局、roots、CLI、stamp、路由、Comment ownership、upgrade/proposal/storage 与安全边界不变。
- [x] 双语语义一致、中文派生一致，generated snapshots/manifest 同步。
- [x] 本地 before/after 回放覆盖上述场景；结果可复核，无已确认的关键行为退化。（fixture 回放 5 场景 × a/b + 场景 6 机械回放；证据 `docs/evals/profile-knowledge-ablation-2026-09/`，对照表见 round-1 返修条目）
- [x] 相关与全量测试、check/status、sync、嵌入脚本一致性、diff 检查通过；任何既有异常如实区分。（213/213；0 error + 1 条预期 `TASK_STORAGE_PENDING` warning）
- [x] 分列 source/英文模板/generated/test LOC 与 bytes 变化；不把更少中文行数或测试绿等同 token/质量改善。
- [x] 无新增 router/schema/state/subsystem；无未关闭 P0/P1/P2，Codex 独立复验 APPROVE 后由 owner accepted。（round-2 四项全部关闭；owner 明确授权验收收尾与本地提交）

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.test_trellium.AgentInitTest scripts.test_trellium.TemplatePackagingTest
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
cmp scripts/trellium.py skills/trellium/assets/trellium.py
cmp scripts/trellium.py skills/trellium-zh/assets/trellium.py
python3 scripts/trellium.py check . --format json
python3 scripts/trellium.py status . --format json
git diff --check
git diff --cached --name-only
git status --short
```

嵌入产品脚本应保持与基线 byte-identical，而不只是三个脚本彼此相同。补跑实际所在类的 Profile upgrade/定制保护测试；字节与行数是静态载荷指标，不虚构 tokenizer 测量。新增 tracked TASK 未提交可能有 `TASK_STORAGE_PENDING` warning，禁止为清 warning 擅自 stage。

## Execution Record

### 2026-09-30 — PI: M0 baseline + deletion candidate table

Baselines frozen in `/tmp/trellium-task-0026.6Cw5Ns`（6 文件 + SHA256SUMS）；只读基线：全量 suite OK、focused 29 OK、check 0 error / 1 warning（新 TASK 未提交的 `TASK_STORAGE_PENDING`，计划已声明且禁止为清 warning 擅自 stage）。快照字节：zh Go 213/12205、zh Python 234/9105、en Go 66/7383、en Python 45/4959。

分类短表（组归并；DELETE=候选判断，REPO-DERIVED 须标事实来源与 fallback）：

| 原位置 | 判定 | 原失败模式 | 删除后防线/证据 |
|---|---|---|---|
| Go 模块和依赖管理 · 常用命令块（init/get/tidy/download/list） | DELETE | 命令名记忆型教程，非决策 | 约束 bullet 已含“依赖变更后 `go mod tidy` 并审查 diff”；缺失时 `go help mod` |
| Go 进入项目时先确认 · `go version`/`go env` 命令块 | DELETE | 环境发现教程 | 执行原则 5 条保留（构建契约优先、workspace 识别、build tags）；事实来源为仓库 `go.mod`/`go.work`/CI + 实际 `go env GOMOD GOWORK` 查询（round-1 P2 更正：`go help environment` 是通用帮助，不能确定当前环境） |
| Go 推荐结构 · 两个目录树 code block | DELETE | 示意骨架与 bullet 重复 | 目录边界 bullet 保留 cmd/internal/pkg/命名/import cycle 约束 + “只创建当前任务需要的目录” + “既有项目优先沿用”（M3 场景 1/4） |
| Go 分层和依赖方向 · 箭头图 | DELETE | 示意图与下方 4 条约束重复 | 约束逐层描述职责与接口最小化原则 |
| Go 测试 · `gofmt -w`/`go test`/`go vet` 命令块 | DELETE | 命令教程 | “按变更范围追加检查” 5 条 + 完成标准保留验证语义；run-directory 约束段（根目录一次测试≠全 module）**必须保留**（M3 场景 3 否决条件） |
| Go 测试 · “`*_test.go` 命名”“默认标准库 testing/表驱动”两条 | DELETE | 基础语法知识 | 其余 8 条测试决策约束保留（同包 vs `_test`、`t.Parallel` 无共享、httptest/fake、外部调用禁止、race 覆盖、fuzz 边界） |
| Go 定位/默认技术栈/进入原则/模块约束/目录边界/分层约束/风格/错误/资源/并发/HTTP/测试约束/完成标准 | KEEP | — | 高信息增益决策约束与风险约束；`%w`/`errors.Is`/`t.Cleanup` 等字面词所在 bullet 均为可执行语义，保留 |
| Py 进入项目时先确认 · `uv sync`/版本命令块 | DELETE | 环境发现教程 | 执行原则 4 条保留（pyproject/uv.lock 构建契约、入口发现、沿用既有配置、文档差异）；事实来源为仓库 `pyproject.toml`/`uv.lock`/CI + 当前解释器、入口的实际查询（round-1 P2 更正：`python --help` 是通用帮助，不能确定解释器/入口） |
| Py 包管理 · 允许命令块（add/sync/run/lock） | DELETE | 命令教程 | 约束 bullet 已含“依赖变更后 `uv sync` 并审查 `uv.lock`”；uv 整合偏好 bullet 保留 |
| Py 推荐结构 · 目录树 code block | DELETE | 示意骨架 | 分层约束逐层保留 + “只创建当前任务需要的目录” |
| Py 分层和依赖方向 · 箭头图 | DELETE | 与 6 条约束重复 | 约束保留全部层职责与 DI 禁令 |
| Py API 规范 · 统一响应/Pydantic/Settings 三个代码例 | DELETE | 示例代码载荷 | 对应语义 bullet 保留（Pydantic 模型定义响应→文档准确、Field description、model_config 非 v1、env_prefix、密钥经 env/kms 不入库）；API 文档表达归 Comment Policy（TASK-0025 已定边界） |
| Py RESTful URL 4 条 bullet | KEEP | 公共契约偏好 | 行为/偏好语义，M3 场景 5 对照 |
| Py 代码质量工具 · 命令块 + 重复的“版本下限由 pyproject 决定” | DELETE/合并（REPO-DERIVED） | 入口/版本发现教程；与默认技术栈表重复 | 事实来源：项目 `pyproject.toml`/pre-commit；fallback：缺配置时 Black/isort/flake8、行宽 120 的原偏好保留；pre-commit “有则沿用无则不引入”保留。round-1 记录更正：原表把“flake8 具体参数”也归入本行删除，与实际不符——flake8 `max-line-length=120`/`max-complexity=10` bullet 实际 KEEP（判定应为：命令块与重复叙述 DELETE，flake8 具体参数 KEEP） |
| Py 测试 · `uv run pytest`/`--cov` 命令块 | DELETE | 命令教程 | 测试 5 条约束保留（conftest、mock 外部、httpx 不监听、覆盖率由项目定） |
| Py 定位/默认技术栈/包管理约束/风格/异步资源/错误/测试约束/完成标准 | KEEP | — | uv/FastAPI/Pydantic 偏好保留；资源/取消/错误/密钥边界保留 |

MOVE：本轮无（禁止新增载体）。REPO-DERIVED 均标了来源与 fallback。

M0 冻结的 before/after 场景（与计划 M3 表一致）：每场景固定 task/repo 输入，仅替换消融前后 Profile，记录可检查结果（见 M3）。判定标准：后版不得强推默认栈/额外依赖、不得因“repo 可推导”丢失 fallback、不得漏掉任一保留风险约束、行为约束仍在 Profile 而表达仍归 Policy、upgrade/proposal 语义不变。

### 2026-09-30 — Codex: planning only

- Owner 确认 Decision 可以推翻，要求任务文档交 PI 执行。本轮仅建立契约与最小记忆更新。
- 只读评估：中文 Go 213 行/12205 bytes、Python 234 行/9105 bytes；英文 Go 66 行/7383 bytes、Python 45 行/4959 bytes。英文已压缩叙述，须以语义和实际载荷判断，不追求统一行数。
- 计划创建前聚焦 29 tests OK，sync in sync；check 0 error/0 warning。没有执行消融、行为回放或全量 suite；M0 由 PI 重测冻结。


### 2026-09-30 — PI: M1–M3 complete (ready_for_review)

M1 消融（zh canonical + 等价 en 模板；zh 模板由 `write_derived_profiles` 机械派生、byte-identical 验证）：

| 文件 | lines | bytes |
|---|---|---|
| source go (zh) | 213 → 158 | 12205 → 11597 (−608) |
| source python (zh) | 234 → 144 | 9105 → 7427 (−1678) |
| en template go | 66 → 66 | 7383 → 7294 (−89) |
| en template python | 45 → 45 | 4959 → 4861 (−98) |
| zh templates (derived) | 同 canonical | 同 canonical |
| generated mirror | == canonical（sync `--check` in sync） | |
| test delta | +1 方法（61 insertions，kept-constraint 冻结） | |
| init/ 源 | 2 消融 + MIGRATIONS 新增 1 节（15+/156−） | |

M2：MIGRATIONS 新增 `Unreleased — profile knowledge ablation (Round 2)`（内容变化 + 定制保护不变声明）；`test_profiles_keep_decision_constraints_after_knowledge_ablation` 双向冻结（保留 marker 在位 + 已删载荷缺席）；不涉及 D-0011 复评（本轮只改内容策展，不改存储/布局判断，无冲突）。

M3 决定性约束对比回放（baseline `/tmp/trellium-task-0026.6Cw5Ns` vs 当前，六场景）：

> round-1 更正：下表前五行是关键词/决定级对照，不是契约要求的行为回放；当时把 behavioral_replay 标 passed、并把 Agent-tool 级 A/B 降为“可选补充”均不成立（review P1）。行为回放由下方 round-1 返修条目的 fixture 回放承载，本表仅留作静态对照记录。

| 场景 | 证据 | 结果 |
|---|---|---|
| 1 低风险修改/已有布局 | `既有项目优先沿用` base=1 now=1（双 profile） | PASS，无“强推默认栈” |
| 2 新项目/缺配置 | `## 默认技术栈` base=1 now=1（双 profile），uv/FastAPI/标准库偏好在位 | PASS，fallback 未丢 |
| 3 多 module/workspace | `不要假设从仓库根目录运行一次` base=1 now=1 | PASS，run-directory 约束保留 |
| 4 并发/取消/资源 | `%w` base=1 now=1；`channel` base=3 now=3 | PASS，风险约束未漏 |
| 5 API/边界/表达归 Policy | `Comment Policy` base=1 now=1（双 profile）+ 新冻结测试 | PASS，无重复 owner 回归 |
| 6 定制 upgrade/proposal | `UpgradeMechanismTest` 全绿（真实机械回放：定制 profile → proposal 路径不变） | PASS |

诚实边界：未执行跨两个 profile 版本的真实模型 A/B（计划明示无须大型 benchmark）；行为 gate 依据为“决定性指令前后逐字一致 + 保护测试绿”的决定级回放，未来 Agent 行为由同指令推导。~~Agent-tool 级 A/B 属可选补充~~（round-1 撤回：该判断被 review 否决，fixture 行为回放为 gate 必需证据，见下方返修条目）。

Checks run: 计划 Verification 块全部执行（结果见下）。

Next action: Codex review；owner 决定 accepted。按 Ownership 不自行 commit。

### 2026-09-30 — PI: round-1 review 返修（P1 fixture 行为回放 + 3×P2）

Review round 1 = REQUEST_CHANGES（1×P1、3×P2，无 P0）。逐项返修：

**P2-2 zh Go 依赖方向**：`init/protocol/profiles/go-backend.md` 分层节补一句“依赖方向：Transport（HTTP handler）→ Application / Use Case → Domain Logic；Adapter 实现 Application 拥有的最小接口并对接外部系统。”（不恢复箭头图；en 模板本就保留，未改）。kept-constraint 测试补双向冻结 marker（zh `Application / Use Case → Domain Logic`、en `transport to application/use-case to domain`）。

**P2-3 事实来源**：Go 行改为“仓库 `go.mod`/`go.work`/CI 配置与当前工具链的实际查询（如 `go env GOMOD GOWORK`）”；Python 行改为“仓库 `pyproject.toml`/`uv.lock`/CI 配置与当前解释器、入口的实际查询”；不再引用 `go help environment`/`uv run python --help`（通用帮助 ≠ 环境事实）。M0 表对应两行同步更正，zh 模板与 protocol-source snapshots 由 sync 派生。

**P2-4 记录更正**：`vault/runtime.md` Current Phase/Progress/Next Steps 改为与交付一致（Profile 已实施；原“六场景回放 green”更正为决定级对照；Next Steps 改为返修后停在 ready_for_review）；M0 flake8 行判定更正为“命令块/重复叙述 DELETE + flake8 具体参数 bullet KEEP（原表整行标 DELETE 与实际不符）”；AC 逐项标注。

**P1 fixture 行为回放**：证据包 `docs/evals/profile-knowledge-ablation-2026-09/`（`protocol.md`/`prompts.md`/`fixtures/`/`build-replay.sh`/`capture.sh` + `runs/` 原始输出 30 个文件）。设计：5 场景 × a/b；固定 task 文本与 fixture，两侧除 `AGENTS.md` 外逐字节一致（`diff -r` 已验证）；a=`git show HEAD:` 消融前 Profile，b=当前（含本轮 P2 修改）；同 agent（fresh `worker`）单次并行执行；目录名 a/b 中性，映射只在 protocol/build 脚本。每运行产出全量 `git diff <基线SHA>`、RUNLOG、最终报告与独立客观验证。

| 场景 | a（消融前）与 b（消融后）实际行为 | 否决条件 | 判定 |
|---|---|---|---|
| s1 healthz（Go 既有仓库） | 两侧均：先 `go env` 确认单 module、零新增依赖、沿用 `writeJSON`/`internal/httpapi`、跑 `make verify`、无新目录 | 后版强推默认栈或额外依赖 | 未触发；两侧 `make verify` PASS |
| s2 空仓库起服务（Py 无配置） | 两侧均：uv + FastAPI + Pydantic v2 + pytest/httpx 显式按 Profile 默认栈，只建任务需要的文件；均引用 fallback 偏好 | 以“repo 可推导”丢 fallback 或超需初始化 | 未触发；两侧 AST/测试验证 PASS |
| s3 go.work 双 module | 两侧均：明确根目录 `go test ./...` 不覆盖 → 逐 module 验证；均修出正确 `Discount` 公式（不同等价写法） | 根目录一次测试被误当全覆盖 | 未触发；两侧 moda+modb `go test` PASS |
| s4 Poller 生命周期 | 两侧均：Stop+等待 goroutine 退出、错误 `%w`+`errors.Is` 不静默、`t.Cleanup`、`go test -race`、零依赖 | 任一保留风险约束漏掉/改变 | 未触发；两侧 vet+test PASS |
| s5 分页 API+注释（Py） | 两侧均：`ge=1`/`le=100`→422 边界、Pydantic v2 `Field(description)`、`response_model`、docstring 补充；6 tests 绿（a 侧反而多 `uv add pydantic`，b 侧零新增依赖） | 安全/兼容退化或重复 owner 回归 | 未触发；两侧 `uv run pytest` 6 passed（round-2 更正：原 fixture 缺 `code-comments.md`，本行当时只支持 API 功能面；补 Policy 后的定向重跑证据见 round-2 条目） |
| s6 定制 upgrade/proposal | `UpgradeMechanismTest` 32/32（pristine 正常刷新、定制只出 proposal 不覆盖） | 覆盖定制或升级语义变化 | 未触发（机械回放） |

结论：六个否决条件均未触发，无已确认关键行为退化；behavioral_replay gate 先降为 `in_progress`，现以上述 fixture 回放证据标 `passed`。

诚实边界：单次 A/B、非盲评、模型随机性存在（两侧结构选择有随机差异：s2 分层形态、s5 是否 `uv add pydantic`——均非 b 侧退化）；s1 并行执行时 a 侧冒烟 server 短暂占用 8080，b 侧如实识别非自身构建、拒绝越权杀进程、改以 httptest 覆盖（`runs/s1b-agent.md`）；harness 非模型级：agent 的工具执行环境与真实 Agent 宿主不同，属“有限行为回放”而非完整产品链路复现。

Checks（返修后重跑）：full suite 213/213；focused `AgentInitTest` 25/25、`UpgradeMechanismTest` 32/32；`sync-skills.py --check` in sync；嵌入脚本 `cmp` byte-identical；`trellium.py check` 0 error / 1 warning（新 TASK 未提交 `TASK_STORAGE_PENDING`，计划内预期）；`git diff --check` clean；`git status` 仅预期改动（未 stage/commit）。

### 2026-09-30 — PI: round-2 review 返修（证据工具 2×P1 + 2×P2）

Review round 2 = REQUEST_CHANGES（2×P1、2×P2，均在证据工具链；round-1 的正文/记录 P2 与 A/B 补证已获确认）。逐项返修：

**P1-1 构建脚本可能误删任意目录**：`build-replay.sh` 删除全部 `rm -rf`；默认 `mktemp -d` 新目录，显式目标已存在即拒绝（exit 2）；脚本只创建、不覆盖、不删除，并新增 scenario 参数支持定向构建。自测见 `tooling-selftest.txt`（重复构建拒绝 exit 2）。

**P1-2 采集无法可靠判定成功**：`capture.sh` 三处修复——(1) 分隔符改为运行时 `printf '\t'` 并对 key/lang/base 做严格校验，解析失败或整行进 key 时点名报错 exit 2（不再依赖源码里的不可见字面量）；(2) s2 移除 `|| true`，pytest 与 AST 各自失败都计入（子步状态不被后续命令覆盖）；(3) 退出码由 verify 结果聚合决定：任一 `VERIFY FAIL` → exit 1。**故意失败 fixture 验证非零退出**：`docs/evals/profile-knowledge-ablation-2026-09/tooling-selftest.txt` —— 构建 exit 0 → 重复构建拒绝 exit 2 → 含内置红 fixture（s3 未修 bug）的采集 `s3a/s3b VERIFY FAIL` → exit 1 → 篡改 map 分隔符 → 解析拒绝 exit 2。另用修复后工具把 round-1 root 原位重采：10/10 VERIFY PASS、exit 0，patch 行数与 round-1 逐项一致。

**P2-3 消融前基线未固定**：`BASE_SHA` 钉为预消融提交 `a01950a1afab092ae4296b29a00c1b9da74fd7ab`，不再用浮动 `HEAD:`（本任务提交后 HEAD 会变成消融后内容）；两侧 Profile sha256 记录在 `docs/evals/profile-knowledge-ablation-2026-09/profiles.sha256`（build 同时写入 replay 根）：before-go `f44b73…7c5`、after-go `284539…c93`、before-python `b814bb…8f00`、after-python `d92c21…0b94`（完整值见该文件与 protocol）。

**P2-4 s5 未实际验证 Comment Policy ownership**：fixture v2 在两侧加入同一份 `docs/engineering/code-comments.md`（由 trellium `render_profile_document` 从 zh 模板渲染、roots=`app, tests`，与目标项目生成物同源；两侧 `cmp` byte-identical，sha256 `22047dca…ede0`）。定向重跑 s5（replay root `/tmp/trellium-0026-replay-r2`，scenario 参数只建 s5；`diff -r` 排除 `.venv` 等环境产物后两侧除 `AGENTS.md` 外逐字节一致）。重跑结果：两侧最终报告均引用该 Policy 指导注释/docstring（s5a 逐条引用其规则“首行摘要+空行+细节、解释 Why、无 TODO 占位”；s5b RUNLOG 记录 `read … docs/engineering/code-comments.md`），边界/兼容面保持（`ge=1/le=100`→422、v2 `Field`、`response_model`），测试 6 passed/9 passed，`runs/{s5a,s5b}-verify.txt` 双侧 VERIFY PASS、capture exit 0。round-1 的 s5 原始采集归档至 `runs/round1-superseded/`（fixture 不完整属机械性无效，按冻结重跑规则取代）。上一条目 s5 行的“表达仍归 Policy”自本轮起由行为证据支持，不再只靠 API 功能面。

证据位置：`docs/evals/profile-knowledge-ablation-2026-09/`（新增 `tooling-selftest.txt`、`profiles.sha256`、`protocol.md` 的“round 2 修订”节、`runs/s5*` round-2 采集与 `runs/round1-superseded/` 归档；`prompts.md` 未改动，固定任务文本保持逐字）。

Checks（round-2 后重跑）：full suite 213/213；`sync-skills.py --check` in sync；嵌入脚本 `cmp` byte-identical；`trellium.py check` 0 error / 1 warning（`TASK_STORAGE_PENDING` 预期）；`git diff --check` clean；未 stage/commit。

### 2026-09-30 — Codex: independent APPROVE and owner acceptance

Round-2 四项返修独立复验通过，无未关闭 P0/P1/P2；owner 随后明确确认 accepted 并授权本地提交，不 push。全量 213/213、聚焦 62/62、sync、嵌入脚本与基线字节一致、diff-check 均通过。隔离临时 fixture 实证：重复构建目标 exit 2、坏分隔符 exit 2、失败测试 exit 1（s2 pytest 失败不被后续语法检查成功掩盖）、修复后的 Go fixture exit 0；固定基线和四个 Profile 哈希一致，s5 两侧 Policy 相同且实际读取，沙箱外本地 pytest 分别 6/6、9/9 通过。单次 A/B 的有限证据边界保留。验收时 check 为 0 error / 2 条预期 `TASK_STORAGE_PENDING` warning（TASK-0026 及并行新增 TASK-0027），非回归；本次仅暂存 TASK-0026 范围，保留并行工作区内容。

提交前全量再跑 213/213，暂存后 check 为 0 error / 1 条 warning（仅并行 TASK-0027）。新增原始 `runs/*-changes.patch`（含 superseded 目录）中的 Git 上下文标记会触发普通空白检查，证据保持字节不变；排除这些原始 patch 的暂存空白检查通过，不改仓库配置。

## Memory Updates

- `vault/runtime.md`：仅 project-global phase、Focus 导航与下一步，不复制状态块。
- `vault/collaboration.md`：记录 Decision 是可复评的留痕，不是不可推翻的约束。
- D-0011：实施形成新判断时才追加最短复评；不新增治理文件。
- Durable knowledge disposition: not_applicable（tracked task）。

## Handoff Requirement

正常交付计划不写 handoff；本任务与 repo state 足以恢复。只有真实中断且有非可推导 transient delta 时写三小节，禁止再写完整进度副本。

## Completion Report

只报告 Deleted/Kept/Repo-derived、对照回放结果、Tests、分列 Net LOC/bytes、Remaining risk；回答：是否把低价值知识移到了新必读载体？是否改变工程偏好、路由或机器状态？预期均为否。
