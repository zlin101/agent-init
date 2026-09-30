# 30 - Agent 入口文件

## 定位

Agent 入口文件是项目级 Agent 指令。

常见文件名：

- `AGENTS.md`
- `GEMINI.md`
- `CURSOR.md`
- `CODEX.md`

默认只生成 `AGENTS.md`；Claude Code 等已支持该标准入口的工具直接读取它，不再创建独立 `CLAUDE.md`。如果其他工具仍需要专属入口文件，它必须与 `AGENTS.md` 保持语义一致。

## 原则

- 入口文件短小、稳定、可执行。
- 入口文件告诉 Agent 如何工作，不承载完整项目历史。
- 动态上下文放入 `vault/`。
- 长工作流放入 `skills/`。
- 技术栈细节放入 profile 或开发文档。
- 工程规则正文放在项目工程文档；入口只做一跳条件路由，不经 Vault 二次转发。

## Required Reading

入口文件必须要求非琐碎任务读取：

```text
vault/index.md    # 含任务等级与授权速查表
vault/runtime.md
```

任务为 Level B 或 Level C、等级或授权判定模糊、或任务涉及治理规则本身时，追加读取完整：

```text
vault/governance.md
```

第一次进入项目追加读取：

```text
vault/project.md
```

接手真实中断的任务追加读取（可推导的干净会话边界不读）：

```text
vault/handoff.md
```

用户提到挂起、搁置或暂停的事项时追加读取：

```text
vault/parked.md
```

追踪任务或治理任务追加读取：

```text
vault/tasks/<task-id>.md
```

修改或评审源码、公共 API、依赖、构建、并发或生命周期行为时，读取 `docs/engineering/profiles/` 下 root 与当前路径匹配的 profile，只应用当前文件实际语言的 profile；纯注释/文档工作（注释、Doc Comment、docstring、TODO/FIXME、directive 排布）只读 Comment/API Documentation Policy `docs/engineering/code-comments.md`；公开 API 变化或行为与注释同时修改时两者并读，表达规范以 Policy 为准。非工程任务不加载这些正文。

## 必备工作规则

入口文件必须要求 Agent：

1. 读取必要上下文；
2. 判断任务等级和授权等级；
3. 明确任务边界和验收标准；
4. Level B 或 Level C 任务创建或更新任务文件；状态变化只更新任务文件的 `trellium-task-state` 状态块；
5. 做最小必要修改；
6. 行为变化时补充或更新聚焦测试；
7. 运行必要检查；
8. 检查验收门；
9. 更新 `vault/runtime.md`；
10. 长期有效决策更新 `vault/decisions.md`；
11. 仅在真实中断且存在非可推导 transient delta 时更新 `vault/handoff.md`；
12. 用户挂起任务时记入 `vault/parked.md`，重新提起时升回。

`storage_mode=local` 或 `private` 的项目在 fresh clone 中缺少 local TASK 文件符合 storage contract；`runtime.md` 不承担恢复副本职责。继续该任务前先向 owner 取回原任务文件，或经 owner 批准后重建任务契约。

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
