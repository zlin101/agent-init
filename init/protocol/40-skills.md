# 40 - Skills

## 定位

`skills/` 保存可复用 Agent 工作流。

Agent 入口文件不应承载复杂工作流细节。当任务明显匹配本地 skill 时，Agent 应读取并执行该 skill。

## 推荐初始 Skill

初始保持克制：

```text
skills/
  agent-task/
    SKILL.md
```

任务 skill 应覆盖：

- 必要上下文读取；
- 任务等级和授权等级判断；
- 计划先行和上下文扎根；
- 任务边界和验收标准；
- Level B / Level C 任务文件创建；
- 可恢复检查点；
- 聚焦实现；
- 验证；
- vault 更新；
- handoff 更新。

## INIT 应用 Skill

当需要把本协议作为可复用能力交给后续 Agent 执行时，可以新增：

```text
skills/
  agent-native-init/
    SKILL.md
```

该 skill 的职责是应用 `init/` 协议源，而不是复制或替代协议源。它应覆盖：

- 新项目初始化与既有项目接入的模式选择；
- 必需读取的 `init/INIT.md` 和 `init/protocol/*` 模块；
- 接入模式下默认只修改 Agent 协作层的边界；
- 初始化或接入前的任务契约；
- 完成前的多轮 review 和反思；
- 验证、vault 更新和剩余风险汇报。

如果 `agent-native-init` 与 `init/` 协议源发生冲突，以 `init/` 为准，并更新 skill 使其重新对齐。

## 开源 Skill 包

当目标是发布、安装或迁移一个不依赖本仓库 `init/` 路径的自包含 Skill 时，使用：

```text
init/skills/agent-native-init/
init/skills/agent-native-init-zh/
```

该包应包含：

- 简短的 `SKILL.md` 主流程；
- `references/` 中的协议模型和模板使用说明；
- `assets/templates/` 中的 Agent 入口、vault、任务规则和 starter skill 模板；
- `agents/openai.yaml` UI 元数据。

开源 Skill 包应提炼协议精华，不逐字复制当前沙盒状态；不得包含本地绝对路径、密钥、个人工具配置或目标项目特定事实。

`agent-native-init` 是英文版，`agent-native-init-zh` 是中文版。两者语义应保持一致，除语言本地化外不应分叉。

## 后续 Skill

只有当重复工作流价值明确时再添加：

- `context-triage`
- `decision`
- `handoff`
- `review`
- `debug`
- `release`

不要在读取路径尚未稳定前创建大量 skill。

当同类工作流重复两次以上，且步骤、检查清单和失败模式已经稳定时，优先沉淀为聚焦 skill，而不是继续扩写入口文件或依赖临时提示词。
