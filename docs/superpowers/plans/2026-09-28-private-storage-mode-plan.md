# Trellium Private Storage Mode 最终实施计划

- 日期：2026-09-28
- 需求：在 `tracked`、`local` 之外增加用户可选的 `private`，使 Trellium 管理的材料不进入 Git 或远端。
- 实施 Agent：PI
- 状态：方案反思、消融与 red-team 已完成；产品代码尚未修改。
- 任务：`vault/tasks/TASK-0019-private-storage-mode.md`

## 1. 结论

实现 `private`，但不把它伪装成第三种 TASK storage。它是整个 Trellium 协作层的存储模式：协作核心、项目记忆、TASK、review、profile、升级提案和安装 stamp 都只存在于当前 worktree。

用户仍只面对三个选项：

| 模式 | Trellium core | TASK / review / archive | 主要用途 |
| --- | --- | --- | --- |
| `tracked` | 进入 Git | 进入 Git | 团队共享完整协作流水 |
| `local` | 进入 Git | 不进入 Git | 默认；共享长期真相，私有工作日志 |
| `private` | 不进入 Git | 不进入 Git | 不希望目标仓库出现任何 Trellium 管理材料的个人使用 |

默认保持 `local`。`private` 不是加密、访问控制、历史清除或防泄漏系统；它只建立并机械验证 Git 边界。

## 2. 对初步方案的反思

### 2.1 初步方案中成立的部分

- `private` 与 `local` 有真实差异：local 仍公开 core，private 连 core 也不进入 Git。
- `.git/info/exclude` 是正确的默认载体：它属于当前 clone，不会为了表达“不上传”而先上传一条 `.gitignore` 规则。
- checker 必须理解 private，否则 TASK-0013 的 durability Gate 会把正确 private 状态误报为 core 丢失。
- tracked `AGENTS.md` 是严格 private 的硬冲突：Git 不能忽略一个已跟踪文件中的局部 marker。
- 存量项目不能自动 untrack，更不能声称从 Git 历史删除。

### 2.2 初步方案中过度或不够准确的部分

- 不能只给 `task_storage` 增加 `private`。该字段只描述 TASK；让一个值隐式翻转全部 core 的持久性会制造隐藏语义。
- 不应让脚本新增交互式 `--storage` 参数。选择仍由 Skill/Agent 一句询问完成；确定性脚本只负责渲染、升级和校验。
- 不应把“所有和 Trellium 相关的文件”解释为扫描任意文本内容。可机械承诺的边界必须是明确 managed scope，而不是猜测文件是否“相关”。
- 不应使用 `skip-worktree`、`assume-unchanged` 或全局 Git exclude。这些手段会隐藏 tracked 修改、影响其他仓库或制造不可审计状态。
- 不应承诺 private 绝不会被上传。`git add -f`、用户手工修改规则或在运行 check 前直接 push 都无法被 Trellium阻止；产品承诺应是“配置边界 + check 检测”，不是安全沙箱。

## 3. 方案消融

### A0：继续使用 local，用户手工忽略整个 Trellium

结果：淘汰。

- 当前 checker 会产生 `CORE_STORAGE_IGNORED` / `CORE_STORAGE_UNCOMMITTED`。
- policy 仍声称 core durable，状态与用户意图冲突。
- Agent 可能按错误修复建议把私有文件重新提交。

### A1：给 schema v1 的 `task_storage` 增加 `private`

结果：淘汰。

- 字段名与实际语义冲突。
- 一个 TASK 字段隐式改变 AGENTS、Vault、Skill、profile 和 stamp 的 Git 契约。
- 后续 checker 和迁移很难区分 TASK 私有与 core 私有。

### A2：增加 `core_storage` 与 `task_storage` 两个正交字段

结果：淘汰。

- 会产生 `core=private + task=tracked` 等无意义组合，需要额外互斥规则。
- 用户只有三个实际模式，不需要暴露二维配置空间。
- 增加策略理解和测试成本，没有当前用例收益。

### A3：policy schema v2 使用单一 `storage_mode`

结果：选择。

```json
{
  "schema_version": 2,
  "storage_mode": "private"
}
```

- 字段名与三种用户模式一致。
- checker 可先规范化 v1/v2，再复用生命周期和预算逻辑。
- legacy schema v1 保持可读，不强制迁移。
- 新模板使用 v2；升级不得只为改 schema 重写现有 policy。

### Entry carrier 消融

| 候选 | 结论 | 理由 |
| --- | --- | --- |
| 修改项目根 `.gitignore` | 淘汰 | 为了声明 private 而向仓库提交 Trellium 配置，违反需求 |
| `.git/info/exclude` | 选择 | clone-local、Git 原生、可由 checker 只读验证 |
| `skip-worktree` / `assume-unchanged` | 禁止 | 隐藏 tracked 修改，merge/upgrade 不可靠 |
| 全局 excludesfile | 淘汰 | 影响其他仓库，边界不可审计 |
| 把全部文件搬到 `.trellium/` | 淘汰 | 普通 Agent 无法通过标准项目入口自动发现，且需第二套布局 |
| tracked AGENTS 指向 ignored 文件 | 淘汰 | tracked 指针本身仍是 Trellium 相关上传内容，不满足严格定义 |

## 4. 精确定义

### 4.1 Managed private scope

private 模式机械保护以下集合：

1. `AGENTS.md`（仅当它由 private adoption 新建，或 adoption 前已经 untracked）。
2. 整个 `vault/`，包括 stamp、tasks、decisions、details、upgrade proposals 和未来 Vault 文件。
3. 整个 `skills/agent-task/`。
4. stamp `files` 中列出的其他 managed 文件，例如选定的 `docs/engineering/code-comments.md` 与 `docs/engineering/profiles/*.md`。
5. Trellium 生成的 `.agent-init-backup/`（如流程会创建）。

不承诺识别用户自行创建、仅在正文中提到 “Trellium” 的任意文件。

### 4.2 Private 的非目标

- 不加密本地文件。
- 不阻止其他本地用户、备份程序、IDE 或 Agent 读取。
- 不清理已存在的 Git 历史。
- 不提供跨 clone 恢复或团队共享。
- 不自动执行 `git rm --cached`、commit、push、history rewrite。
- 不修改全局 Git 配置。

## 5. Policy 兼容设计

checker 内部先把 policy 规范化为 `tracked | local | private`：

- schema v1 + `task_storage=tracked` → `tracked`
- schema v1 + `task_storage=local` → `local`
- schema v2 + `storage_mode=tracked|local|private` → 同名模式

约束：

- v1 只接受既有字段和既有两个值。
- v2 要求 `storage_mode`，拒绝 `task_storage` 与未知字段。
- budgets 在两个版本保持同一语义。
- 现有项目不自动从 v1 改成 v2。
- 新 adoption 在 Agent 完成选择后写 v2。
- repeated adopt / upgrade 保持既有模式；冲突选择必须在写入前停止。

## 6. Agent-native 接入流程

### 6.1 首次询问

Skill/Agent 在 adoption 前询问：

```text
选择 Trellium 存储模式：
- local（默认）：core 进入 Git，TASK 留在本地
- tracked：core 和 TASK 都进入 Git
- private：全部 Trellium managed material 只留在当前 clone
```

owner 未指定时仍选择 local。

### 6.2 Private preflight

在运行 `adopt` 前：

1. 确认目标是否在 Git worktree 中并取得 repo root/target prefix。
2. 检查 `AGENTS.md` 及将要生成的 profile/工程文档是否已经 tracked。
3. 任何需要被 Trellium 修改的 carrier 已 tracked 时，严格 private preflight 失败，且不得产生部分写入。
4. 不使用 `skip-worktree`、`assume-unchanged` 绕过。

第一版不支持把现有 tracked `AGENTS.md` 语义合并为 private；PI 必须输出明确诊断和可选退路，而不是静默降级：

- 改选 local；或
- owner 先自行建立非 Trellium 的本地 Agent 入口机制，再重新评审；或
- 单独立项做存量迁移。

### 6.3 写入与 exclude

preflight 通过后：

1. 正常生成 Trellium 文件和 stamp。
2. Agent 将 policy 写成 schema v2 `storage_mode=private`。
3. Agent 在目标 Git root 的 `.git/info/exclude` 中维护带 target identity 的 canonical private block；通过 `git rev-parse --git-path info/exclude` 定位，不能假定 `.git` 一定是目录。
4. marker 形如 `# trellium-private:start <git-root-relative-target>` / `# trellium-private:end <git-root-relative-target>`；同一 target 只能有一个完整 block，畸形、重复或交叉 block 必须停止。
5. monorepo 使用 Git-root-relative、带 target prefix 的 anchored patterns；block 只允许目标的 `AGENTS.md`、`vault/`、`skills/agent-task/`、`.agent-init-backup/` 与 stamp 其他 exact managed paths。
6. 至少覆盖 `AGENTS.md`、`vault/`、`skills/agent-task/`、stamp 中其他 managed paths 与备份目录。
7. 不创建 `vault/tasks/.gitignore`；整个 Vault 已由 private boundary 覆盖。
8. 运行 checker；只有 private storage finding 为零才算接入完成。

选择和 `.git/info/exclude` 维护属于 Agent-native 工作流，不新增 CLI 交互参数；`trellium.py check` 保持只读。

## 7. Checker 语义

### 7.1 tracked / local

- 保持 2026.09.9 行为与输出不变。
- 现有 fixture 的 finding code、severity 和退出码不得发生漂移。

### 7.2 private

private 跳过“core 必须存在于 HEAD”的正向 durability Gate，改用反向 privacy Gate：

- `PRIVATE_STORAGE_TRACKED` error：任一 private managed path 已 tracked 或 staged，包括 `git add -f`。
- `PRIVATE_STORAGE_UNCONFIGURED` error：canonical target block 缺失/畸形/重复，或任一必须保护的现有路径与未来 namespace sentinel 未被 ignore。
- `PRIVATE_STORAGE_OVERREACH` error：canonical target block 包含 allowlist 以外的 pattern、非 anchored pattern 或覆盖目标外路径；不要尝试从任意用户 ignore 规则猜测意图。
- `PRIVATE_STORAGE_UNVERIFIED` error：Git 查询失败，无法验证 index/ignore 边界。
- 非 Git 目标使用 warning，说明不存在 Git 上传面，但 privacy boundary 无法机械验证。
- stamp 非法、managed path 非法、symlink/path traversal 等继续使用现有 fail-closed 安全错误，不因 private 放松。

private 检查还必须验证：

- 当前 HEAD tree 不包含 managed paths；否则说明当前版本仍公开这些文件。
- 不扫描全部历史，不声称历史已清除；若当前或过去可能上传过，输出非阻断说明或文档警告。
- `status` 不把 storage finding 当作 lifecycle/authority 来源，保持现有 phase-based unresolved 规则。

### 7.3 TASK lifecycle

private 对 TASK 生命周期采用 local 语义：

- TASK/review/archive 不 tracked。
- 关闭前仍需 knowledge disposition。
- 稳定结论蒸馏到 private Vault 的 canonical 文件；这只提升当前 clone 内可维护性，不声称跨 clone durable。
- closed TASK 从 runtime 热路径删除。
- fresh clone 没有 Trellium，属于预期“未接入”，不是可恢复的 local-task 场景。

相关文案不能继续使用“published truth”或“durable across clone”描述 private 结论。

## 8. Adopt、upgrade 与迁移边界

### Adopt

- 不新增 `--storage` / `--private` CLI 参数。
- 脚本不选择 storage，也不知道调用前的 owner 选择；adopt 结束提示改成模式中立的条件说明：Agent 写入最终 policy 后，tracked/local 检查 HEAD durability，private 检查 untracked + ignored privacy boundary。
- Agent preflight 是 private 模式避免部分写入的前置条件。

### Upgrade / diff / baseline

- private 继续使用本地 stamp 作为 upgrade baseline；policy 不在 stamp 中复制第二份。
- diff/upgrade 不执行 Git index 写入。
- proposal 留在 ignored `vault/.upgrade/`。
- downgrade refusal、managed-file allowlist、symlink/hardlink/path 安全边界全部保持。

### 存量迁移

第一版不自动支持 tracked/local → private：

- 检测到 managed files 已 tracked 时输出迁移提案并停止。
- owner 必须单独批准 index 删除；工具和 Agent不得自动 `git rm --cached`。
- 删除当前 HEAD 文件不等于删除历史。
- 历史清理由独立 Authority 3/4 任务处理，不进入 TASK-0019。

private → local/tracked 同样不自动执行，避免未经授权公开本地记忆。

## 9. 预注册消融与红测

PI 在实现前先提交 M0 契约和 expected-failure 测试；不得先写产品逻辑。

### P0：当前 local + 全量 ignore

- 新仓库真实 adopt。
- policy 保持 local，把 core 加入 `.git/info/exclude`。
- 冻结当前 checker 输出：应出现 core ignored/uncommitted，证明 docs-only 方案不可用。

### P1：private policy + 无 privacy checker

- 只让 parser 识别 private，不改变 storage Gate。
- 预期仍不能达到准确健康状态，证明专用反向 Gate 必要。

### P2：最小 checker-aware private

- schema v2 + policy normalization。
- 反向 privacy Gate。
- Agent-native exclude 契约与条件化 adopt 文案。
- 不新增 CLI 参数、不自动写 Git。

Go Gate：

- P2 在干净 private fixture 中达到 0 error / 0 warning。
- 全部 managed paths 未 tracked/staged且被 ignore。
- `git add -f` 任一 managed path 后必须 error。
- tracked/local 的 check/status golden 与基线一致。
- 不需要 broad ignore、skip-worktree、assume-unchanged 或自动 index 修改。

任一不满足则 No-Go，不通过放松 TASK-0013 安全边界来获得绿色输出。

## 10. 必测矩阵

### Policy

- legacy v1 tracked/local 正常。
- v2 三种 mode 正常。
- v2 缺字段、未知字段、同时出现旧新字段、bool/字符串 schema、未知 mode 全部拒绝。
- existing v1 upgrade 不自动改写。

### Private happy path

- 新 repo、有 HEAD、无 AGENTS。
- 新 repo、无 HEAD。
- monorepo 子目录。
- 显式 Go/Python profile 与多 root。
- repeated adopt 和 repeated check 幂等。
- diff/upgrade/proposal 全部保持 ignored。

### Privacy failures

- 缺少 `.git/info/exclude` block。
- marker block 畸形、重复、target identity 不匹配或 linked-worktree git-path 解析失败。
- 只忽略 Vault、遗漏 AGENTS/Skill/profile。
- managed file 普通 staged、tracked、`git add -f` staged。
- 当前 HEAD 已包含 managed path。
- 过宽 `/docs/`、`/*` 等规则。
- `git check-ignore` / `git ls-files` 失败。

### Entry conflicts

- tracked AGENTS：preflight 拒绝且零写入。
- untracked customized AGENTS：保留内容、添加 marker、整文件 ignored。
- symlink/hardlink AGENTS 或 managed path：拒绝。

### Security regression

- `..`、absolute、malformed、external link、symlink、hardlink。
- selected-profile-only managed authorization。
- anchored dirfd 与 fallback read/hash/write/remove 全部继续 fail-closed。

### Existing modes

- 全部现有 177 tests 通过。
- tracked/local storage fixtures 输出不变。
- embedded bilingual packages、snapshots 与 canonical protocol 同步。

## 11. Red-Team：Top Kill-Assumptions

### R1 — Git ignore 足以表达“private”

- **Claim:** untracked + ignored + checker 检测可以满足“不上传”。
- **Fails if:** 产品文案暗示能够阻止 `git add -f` 或未经 check 的直接 push。
- **Evidence:** 在 fixture 中强制 add 一个 managed file，确认 checker 稳定报 `PRIVATE_STORAGE_TRACKED`。
- **Kill criterion:** 无法在不安装 hook、不接管 Git 的情况下发现 staged/forced-add 状态。
- **Cheapest test:** 一个 private fixture + `git add -f vault/index.md`。

结论：风险成立但可控；收缩承诺为“边界配置与机械检测”，不声称强制防泄漏。

### R2 — 标准 Agent 入口可以保持 private

- **Claim:** ignored `AGENTS.md` 在当前 clone 可被 Agent 正常读取。
- **Fails if:** 目标已有 tracked AGENTS，或目标 Agent 不读取 ignored/untracked AGENTS。
- **Evidence:** M0 已在 `docs/evals/private-mode-kill-gates-2026-09/` 落盘 Agent discovery 证据；不重跑真人探针（2026-09-29 消融：已有证据足够）。
- **Kill criterion:** 新建 ignored AGENTS 不能被任一受支持 Agent发现，或必须修改 tracked carrier。
- **Cheapest test:** 空 repo 创建 ignored AGENTS，启动无历史会话询问其 Required Reading。

### R3 — schema v2 的收益大于迁移成本

- **Claim:** `storage_mode` 比扩展 `task_storage` 更准确且可兼容。
- **Fails if:** upgrade 会为了格式变化重写所有 v1 policy，或双 schema 导致 checker 分叉。
- **Evidence:** normalization 单元测试；v1 project 的 diff/upgrade byte-preservation fixture。
- **Kill criterion:** 无法把所有后续逻辑统一到一个 normalized mode，或 v1 被自动改写。
- **Cheapest test:** 先只实现纯 `parse_policy → normalized_mode` 函数与表驱动测试。

### R4 — managed scope 足够完整且不会误伤业务文件

- **Claim:** namespace + stamp paths 能覆盖未来 Trellium 材料。
- **Fails if:** 新生成文件落在 scope 外，或 broad docs rule 隐藏业务文件。
- **Evidence:** 从 adopt/upgrade 实际输出集合生成 fixture，对照 exclude coverage；加入非 Trellium docs sentinel。
- **Kill criterion:** 需要忽略整个 `docs/`、项目根或无法枚举的任意路径。
- **Cheapest test:** profile + upgrade proposal fixture，逐路径执行 `git check-ignore -v`。

### R5 — private 仍值得保留 Trellium 的 durable-memory 模型

- **Claim:** 即使不跨 clone，本地 canonical memory 仍改善长会话协作。
- **Fails if:** 用户真正需要的是一次性 prompt，不需要 Vault、任务治理或升级。
- **Evidence:** 在一个不允许仓库改动的真实项目完成一次非琐碎任务，比较 private Trellium 与单 prompt 的遗漏和恢复成本。
- **Kill criterion:** private 必须砍掉大部分核心文件才显得可用，或没有第二次会话恢复价值。
- **Cheapest test:** 已被 H2 淘汰（2026-09-29 消融）：handoff 不再承载会话进度，第二会话恢复走 TASK + Git/工作区 + tests 重放，不依赖 handoff。

### What's Well-Reasoned

- 需求与 local 不重复：local 优化仓库噪声，private 解决 core 也不得上传的隐私/所有权边界。
- 选择 `.git/info/exclude` 与“当前 clone 私有”语义一致，不会把 private 配置本身加入项目提交。
- schema v2 + normalization 让 legacy 兼容只存在于 parser 边界，后续逻辑仍只有一个 mode 概念。
- 先拒绝 tracked carrier 比依赖隐藏 index flags 更诚实，也保持 TASK-0013 的 fail-closed 原则。
- 新模式不自动迁移、不自动写 Git index，不会把隐私选择变成未经批准的数据删除或公开动作。

### What I Couldn't Assess

- Codex 与 Claude Code 当前版本是否都稳定读取 ignored/untracked `AGENTS.md`；M0 必须用真实无历史会话验证，不能只靠文档推断。
- linked worktree、submodule 和非标准 Git dir 环境对 Agent 修改 `.git/info/exclude` 的实际权限；checker 应通过 Git 解析路径并保守失败。
- 真实第三方仓库中已有 untracked AGENTS/profile 路径的冲突频率；第一版选择拒绝 tracked carrier，可能限制可用范围。
- private 两会话恢复相对“一句 prompt”是否有足够增益；该问题影响长期产品价值，但不影响 privacy Gate 的正确性实现。

## 12. 实施里程碑

### M0 — 契约冻结与红测

- 提交本计划、TASK-0019、policy normalization 设计和 P0/P1 expected-failure fixtures。
- 记录当前 tracked/local golden。

### M1 — Policy v2 normalization

- parser 同时支持 legacy v1 与 v2。
- 所有 storage 使用点只消费 normalized mode。
- v1 upgrade byte-preservation 通过。

### M2 — Private privacy Gate

- 实现 private path/sentinel 集合与四类 finding。
- 覆盖 tracked/staged/forced-add、missing ignore、overreach、Git failure。
- 不修改 tracked/local Gate。

### M3 — Agent-native adoption contract

- 双语 Skill、初始化/接入/Vault/governance 协议。
- `.git/info/exclude` marker block 规则与 monorepo prefix。
- tracked carrier preflight 与条件化 adopt 完成文案。
- 不新增 CLI storage 参数。

### M4 — Upgrade、安全与分发

- private diff/upgrade/proposal fixture。
- profile、managed-path、dirfd/fallback 与 link/path 安全回归。
- MIGRATIONS、README、VERSION 与双语 snapshots 同步。

### M5 — 独立 review 与 owner Gate

- 至少两轮 review：协议覆盖；隐私、安全和最小性。
- 无 open P0/P1/P2 后进入 `ready_for_review`。
- 不自动 accepted、commit、push、tag 或发布。

## 13. 预计修改范围

产品实现预计涉及：

- `scripts/trellium.py`
- `scripts/test_trellium.py`
- `init/protocol/10-vault.md`
- `init/protocol/20-governance.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/60-initialization-flow.md`
- `init/protocol/70-adoption-flow.md`
- `init/MIGRATIONS.md`
- `init/VERSION`
- 中英文 README 与 Skill
- 两套 generated protocol snapshots
- 本项目 Vault task/runtime/handoff；验收后新增 durable decision

不应修改业务项目源码、依赖、CI、发布配置或当前 owner 排除文件。

## 14. 验收标准

- 用户只需理解 tracked/local/private 三选一，默认 local。
- private managed scope 定义明确，不做文本内容猜测。
- 新 private adoption 的 managed material 全部 untracked/staged-free 且 ignored。
- forced-add、tracked path、缺 ignore、过宽规则、Git failure 全部 fail-closed。
- tracked AGENTS 冲突在任何写入前失败。
- private 不依赖 root `.gitignore`、global config、skip-worktree、hook 或自动 Git index 修改。
- `.git/info/exclude` target block 唯一、可解析、anchored 且只含 approved managed scope。
- legacy v1 完整兼容且 upgrade 不自动迁移。
- tracked/local check/status 行为与退出码无变化。
- upgrade、profile、managed-path 和全部 link/path/fallback 安全边界无回归。
- 全量测试、snapshot、whitespace 与独立 review 通过，无 open P0/P1/P2。
- 文档明确：private 不加密、不清历史、不跨 clone 恢复，也不能绝对阻止用户强制上传。

## 15. 给 PI 的执行指令

先做 M0，不要直接写最终实现。若 characterization 证明 ignored AGENTS 无法被受支持 Agent 发现，或 checker 无法捕获 forced-add，立即停止并回报，不得用 tracked bootstrap、skip-worktree、hook 或放松 TASK-0013 Gate 绕过。

实现中任何需要自动 untrack、修改现有 tracked AGENTS、重写 Git 历史、增加 CLI storage 参数或扩展 private scope 到不明确业务路径的变化，都属于范围扩大，先交 owner 决定。
