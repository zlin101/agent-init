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
- 任务边界和验收标准；
- Level B / Level C 任务文件创建；
- 聚焦实现；
- 验证；
- vault 更新；
- handoff 更新。

## 后续 Skill

只有当重复工作流价值明确时再添加：

- `context-triage`
- `decision`
- `handoff`
- `review`
- `debug`
- `release`

不要在读取路径尚未稳定前创建大量 skill。
