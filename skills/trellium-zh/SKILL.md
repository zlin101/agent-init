---
name: trellium-zh
description: 用于为新项目或既有软件项目添加或升级持久的 Agent 协作规则、项目记忆、任务治理、交接机制或验收审查门。
---

# Trellium 中文版

## 概览

为项目安装和升级 Agent-native 协作层：简洁的 Agent 入口规则、vault 项目记忆系统、任务契约治理、handoff、可复用工作流和审查验收门。

本 Skill 是自包含包。目标项目不需要存在 `init/` 目录。

## 必读 Reference

编辑目标项目前，先读取本 Skill 自带的 reference：

- `references/protocol-model.md`：核心概念和验收门。
- `references/templates-guide.md`：如何使用模板。

`references/protocol-source/` 是从仓库自动生成的权威协议快照，并保留完整的 `init/...` 路径。按任务读取：

- 新项目初始化：读取 `references/protocol-source/init/protocol/60-initialization-flow.md`。
- 既有项目接入：读取 `references/protocol-source/init/protocol/70-adoption-flow.md`。
- 项目类型明确：读取 `references/protocol-source/init/protocol/profiles/` 下匹配的 profile。
- 任务涉及特定治理主题：按 `references/protocol-source/init/INIT.md` 路由到对应协议模块，并将其中的 `init/...` 路径解析到 `references/protocol-source/` 下。

精简 reference 与权威协议冲突时，以 `references/protocol-source/init/` 为准。不要直接修改该生成目录。

使用 `assets/templates/` 下的文件作为起点。必须根据目标项目替换项目名称、检查命令和真实事实，不要盲目复制占位内容。

## 模式选择

编辑前先选择一种模式：

- **新项目初始化**：目标项目为空、可丢弃，或用户明确要求创建新的 Agent-ready 脚手架。
- **既有项目接入**：目标项目已有源码、依赖、测试、构建文件、部署文件、CI 或项目文档。

不确定时，选择既有项目接入。它更安全，因为默认只新增或合并 Agent 协作层。

## 安装与升级（内置脚本优先）

本包自带确定性安装/升级脚本 `assets/trellium.py`，优先使用；Agent 语义迁移在脚本之上叠加。

- 新项目或既有项目首次接入前，先询问 owner 选择 TASK storage，推荐并默认 `local`；owner 未指定时按 local 执行。local 只把 `vault/tasks/TASK-*.md`、review 台账和 archive 留在本地，协作核心仍进入 Git；需要共享完整任务流水时选择 `tracked`；需要 Trellium 完全不进 Git 时选择 `private`（流程见本条后半）。Agent 运行 `python3 assets/trellium.py adopt <target>` 后，把选择写入 `vault/index.md`；local 模式再创建窄范围 `vault/tasks/.gitignore`（`TASK-*.md`、`*-review.md`、`archive/`），tracked 模式不添加这些 ignore 规则。local/private 接入完成身份绑定（local 的 policy/窄范围 ignore 或下述 private 的 policy/exclude 就位后、check 之前）：调用与 `assets/trellium.py` 同目录的 bundled 身份 helper，例如 `python3 -c "import importlib.util as u, sys, pathlib; s = u.spec_from_file_location('trellium', 'assets/trellium.py'); m = u.module_from_spec(s); s.loader.exec_module(m); print(m.ensure_project_identity(pathlib.Path(sys.argv[1]), authorize_create=len(sys.argv) > 2 and sys.argv[2] == '--create'))" <target> [--create]`——有有效 `vault/project-id` 时复用并补登记；缺失但已有绑定证据（版本戳 inventory 或 Git HEAD）时要求恢复原身份，首次绑定授权也不得绕过；fresh 接入在接入计划中说明身份创建，存量 local/private 首次启用先取得 owner 绑定确认；身份创建后登记失败会保留身份文件，重试复用同一 UUID。随后运行 check，0 error 才算接入完成。local/private 任务的 closure retention 使用同目录的 `assets/history_store.py`（标准库模块，无 CLI；默认 root `~/.trellium/history`，必须位于工作 clone 外）：terminal 后把 TASK 与已开展的 review ledger 成组分别 `put` 并 `get` 验证，整组成功才算 retention 完成；失败保留 source 幂等重试，accepted 不回滚；默认不 cleanup，删 source 需 owner 明确授权。Private 的 project-id 保持 ignored，并在 helper 写入前校验 private 边界；登记后 UUID bytes 与 baseline 不符时要求恢复。tracked 不做身份绑定与外部 retention。脚本默认只补缺失文件；已有 `AGENTS.md` 时追加标记区块，不覆盖。语言已明确时重复传入 `--profile go-backend=<root>` / `--profile python-backend=<root>`；每个已选 profile 在 `docs/engineering/profiles/` 生成完整项目文档，并由 AGENTS 按 root 一跳路由；`docs/engineering/code-comments.md` 是项目的 Comment/API Documentation Policy（注释/API 文档表达规范的唯一 owner，重叠规则以它为准；完整规则见 `references/protocol-source/init/protocol/70-adoption-flow.md`「Profile 工程规范」）。不自动猜测语言。Private 存储（policy `storage_mode=private`）让全部目标 managed material 不进 Git，terminal TASK/review 的历史副本可保全到本机 Store：`adopt` 之前先调用 bundled 脚本的只读 `private_preflight(target, profiles)` 探针——例如 `python3 -c "import importlib.util as u, sys, pathlib; s = u.spec_from_file_location('trellium', 'assets/trellium.py'); m = u.module_from_spec(s); s.loader.exec_module(m); print(m.private_preflight(pathlib.Path(sys.argv[1]), profiles=tuple(sys.argv[2:])))" <target> [profile-id ...]`（输出路径或抛错即中止；Git 查询失败 fail-closed）；`adopt` 之后写入 schema v2 private policy，并在 `.git/info/exclude` 维护 canonical `trellium-private` block（anchored patterns、target identity、不允许 overreach 或后置 negation）；永不提交目标 Trellium material；接着调用上面的身份 helper，保持 project-id ignored；运行 `check`，0 error 才算接入完成。Private TASK 使用 local lifecycle 语义；fresh clone 没有 Trellium 属于预期。
- 协议内容更新无需重装本 Skill：adopt/diff/upgrade 命令加 `--fetch` 即从 GitHub 拉取最新 tag release 并以该版本的脚本与模板执行（缓存于 `~/.cache/trellium/`，降级会被拒绝）。重装 Skill 仅在 SKILL 工作流或脚本自身变化时需要。
- 已接入项目的升级：
  1. `python3 assets/trellium.py diff <target>`——只读报告：会动什么、绝不动什么、待执行迁移手册。
  2. `python3 assets/trellium.py upgrade <target> --apply`——执行安全子集；冲突生成提案到目标项目 `vault/.upgrade/<version>/`。
  3. Agent 按提案做语义合并（逐条保留项目定制），用户逐条确认。
  4. `python3 assets/trellium.py upgrade <target> --complete`——收尾登记。
- 无版本戳的存量项目（`vault/.agent-init.json` 不存在）先运行 `python3 assets/trellium.py baseline <target>`。
- 校验项目状态：`python3 assets/trellium.py check <target>`（可加 `--format json`）完全只读、确定性，校验最小状态层——Level B/C 任务文件中 canonical 的 `trellium-task-state` 状态块、`vault/index.md` 的 `trellium-policy` 策略块、热文件预算测量、TASK storage 与 Git 实际状态。`status` 直接扫描这些状态块；runtime Focus 只有导航语义。退出码：有 error 为 `2`；仅 warning 为 `0`（warning 必须显示，不存在无条件 PASS）；操作错误为 `1`。它不自动修复、不写任何文件；没有状态块的历史 TASK 按 unresolved 报告，不猜测状态。新建任务用带状态块的模板，重新激活旧任务时补状态块，不批量迁移历史。在 `local` 项目中，fresh clone 缺少任务文件符合 storage contract；runtime 不提供恢复副本。
- 数据保护：runtime、handoff、decisions、tasks 等项目数据对脚本只读，永不被模板替换；数据文件的格式迁移按 `references/protocol-source/init/MIGRATIONS.md` 语义执行，只做内容搬运，不丢事实。
- 版本判断：目标项目 `vault/.agent-init.json` 的 `protocol_version` 低于 `references/protocol-source/init/VERSION` 时提议升级。
- 脚本无法运行时（缺少 python3 等），回退为本 SKILL 的 Agent 驱动流程：按 `references/protocol-source/` 的协议规则手工合并模板与执行迁移，遵守相同的数据保护边界。

## History 保全与 Private 恢复

Local/Private terminal TASK 与必要 review 台账使用同一 Store。先确定完整的成组来源并冻结内容；从本包目录执行下面的 Python 调用（替换项目与来源路径；只处理已 terminal 的任务，未开展 ledger review 时不要虚构台账）：

```python
import importlib.util
from pathlib import Path

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

trellium = load("trellium", "assets/trellium.py")
history = load("history_store", "assets/history_store.py")
clone = Path("/path/to/project").resolve()
project_id = trellium.ensure_project_identity(clone)["identity"]
store = history.Store(Path.home() / ".trellium/history")
sources = (
    (clone / "vault/tasks/TASK-0001-example.md", "TASK-0001"),
    (clone / "vault/tasks/TASK-0001-review.md", "TASK-0001-review"),
)
results = [history.retain_terminal(store, project_id, source, clone, artifact_id)
           for source, artifact_id in sources]
if not all(result["retained"] for result in results):
    raise RuntimeError("Incomplete group retention; keep every source and retry")
```

逐份 put/get 成功才算整组保全完成。任何失败保留全部 source，幂等重试；默认不 cleanup。历史不恢复任务状态或 Authority，不进入默认读取，不备份当前 Vault。

Private 的 `vault/project-id` 随 Vault ignored，没有 Git 恢复副本；owner 必须保留原 UUID。删除 clone 后仅按已知 UUID、artifact id 和 digest 调用 `store.get(project_id, artifact_id, digest)`，返回原始 bytes 并校验内容；UUID namespace/metadata 是历史归属，不自动成为当前项目身份。重建 private 接入时先完成 preflight/adopt/policy/exclude，由 owner 确认项目并 get 核对历史，再以独占创建（`open("x")`，不覆盖已有文件）恢复原 UUID 加换行到 `vault/project-id`，调用上面的 identity helper **不加 --create** 复用并登记；原 stamp 仍有绑定时也必须恢复同一 UUID。身份已登记但缺失或 baseline 不符时拒绝替换。

没有原 UUID 或确定的项目证据时停止恢复，不按目录、remote 或“最新历史”猜测，也不通过新 UUID 冒充旧绑定。新机器的默认位置仍为该机器用户的 `~/.trellium/history`；迁移 Store 和原 UUID 是显式手工迁移，没有自动同步。存量 Private 首次启用/旧记录回填由 owner 决定；默认仍 Local。

## 任务契约

编辑前先说明：

- 目标
- 模式
- 范围和不做范围
- 预计修改的文件
- 授权等级和需要用户确认的事项
- 验收标准
- 验证命令

如果项目已有 `vault/tasks/`，创建或更新任务文件。否则先在工作说明中保留任务契约，等 vault 创建后再写入 `vault/tasks/`。

## 新项目初始化

创建最小可用项目：

1. 添加 Agent 入口文件，例如 `AGENTS.md`；只有有用时才添加工具专属入口文件。
2. 添加必需的 `vault/` 文件。
3. 添加 `skills/agent-task/SKILL.md`。
4. 只有当用户要求具体项目类型时，才添加源码、测试、依赖和 README。
5. 运行最小有意义检查。
6. 在 `vault/runtime.md` 记录当前状态，在 `vault/decisions.md` 记录长期选择。

项目真正需要前，不要添加框架、服务、数据库、CI、部署、LLM SDK 或凭据。

## 既有项目接入

保护既有项目：

1. 先只读扫描：根目录文件、Agent 入口、README/docs、源码结构、依赖文件、测试、构建/部署/CI 文件、既有记忆或决策记录、工作区未提交状态。
2. 先给出接入计划，只列 Agent 协作层修改。
3. 合并既有 Agent 入口规则，不直接覆盖。
4. 创建或合并 `vault/` 文件和 `skills/agent-task/SKILL.md`。
5. 在 `vault/project.md` 记录这是既有项目接入。
6. 在 `vault/runtime.md` 记录接入状态、风险和下一步。

没有用户明确授权时，不要修改业务源码、测试、依赖文件、锁文件、构建文件、部署文件、CI、数据库迁移、环境文件或大段既有文档。

## Review And Reflection

宣布完成前至少跑两轮。

### Round 1 - 协议覆盖审查

检查：

- Agent 入口文件会将非琐碎任务路由到 `vault/index.md` 和 `vault/runtime.md`，并在 Level B 或 Level C、判定模糊或涉及治理规则时路由到 `vault/governance.md`。
- 必需 vault 文件存在。
- governance 覆盖任务等级、授权等级、任务契约字段、验收门、升级规则和 handoff。
- `skills/agent-task/SKILL.md` 存在，并聚焦任务执行。
- `vault/runtime.md` 是短当前状态，不是长日志。
- `vault/decisions.md` 记录长期选择。
- 需要协作偏好时，`vault/collaboration.md` 存在。
- 热文件预算线与压缩流程由 `vault/index.md` 路由（见 `references/protocol-source/init/protocol/15-vault-compaction.md`）。

先修复缺口，再继续。

### Round 2 - 安全和最小化反思

反思：

- 是否有修改超出所选模式？
- 接入模式下是否改动了禁止触碰的工程文件？
- 是否添加了依赖、框架、服务、密钥、本地绝对路径、端口、模型名或凭据？
- 验证命令是否具体且适合项目？
- 剩余风险和需要用户判断的事项是否已记录？

如果发现问题，修复后重复对应轮次。

## 验证

运行任务契约或目标项目 `vault/runtime.md` 指定的验证。

文档级接入优先使用只读检查，例如列出预期文件、搜索关键术语。代码脚手架则运行最小项目测试命令。接入模式下，除非用户授权，不要运行会改变工程状态的命令。

## 完成汇报

汇报：

- 使用的模式。
- 创建或修改的文件。
- 明确未触碰的区域。
- 验证命令和结果。
- review/reflection 结论。
- 剩余风险或需要用户判断的事项。
