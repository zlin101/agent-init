# 30 - Agent 入口文件

## 定位

Agent 入口文件是项目级 Agent 指令。

常见文件名：

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `CURSOR.md`
- `CODEX.md`

默认生成 `AGENTS.md`。如果存在工具专属入口文件，它必须与 `AGENTS.md` 保持语义一致。

## 原则

- 入口文件短小、稳定、可执行。
- 入口文件告诉 Agent 如何工作，不承载完整项目历史。
- 动态上下文放入 `vault/`。
- 长工作流放入 `skills/`。
- 技术栈细节放入 profile 或开发文档。

## Required Reading

入口文件必须要求非琐碎任务读取：

```text
vault/index.md
vault/runtime.md
vault/governance.md
```

第一次进入项目追加读取：

```text
vault/project.md
```

接手交接任务追加读取：

```text
vault/handoff.md
```

追踪任务或治理任务追加读取：

```text
vault/tasks/<task-id>.md
```

## 必备工作规则

入口文件必须要求 Agent：

1. 读取必要上下文；
2. 判断任务等级和授权等级；
3. 明确任务边界和验收标准；
4. Level B 或 Level C 任务创建或更新任务文件；
5. 做最小必要修改；
6. 行为变化时补充或更新聚焦测试；
7. 运行必要检查；
8. 检查验收门；
9. 更新 `vault/runtime.md`；
10. 长期有效决策更新 `vault/decisions.md`；
11. 任务中断或转交时更新 `vault/handoff.md`。

## 禁止内容

不要把以下内容写入口文件：

- 当前任务历史；
- 长调试日志；
- 完整 API 契约；
- 完整架构文档；
- 领域百科；
- 重复交接记录；
- 密钥或凭据。

## 工具专属文件

工具专属入口文件可以添加极短兼容说明，但不能削弱或违背 `AGENTS.md`。
