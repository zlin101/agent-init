# Runtime Context

## Current Phase

替换为当前阶段。

## Focus

- TASK-0001

Focus 是可选导航信息。它不拥有 lifecycle、Authority、slice、Gate 或活跃任务清单。`trellium status` 直接从 `vault/tasks/*` 读取 TASK 状态。Focus 指向不存在的 TASK 时，只表示导航无法解析。

## Current Progress

- 替换为简短的项目全局当前状态。

## Constraints

- 保持本文件短小。
- 将长执行历史移到 `vault/tasks/*`。
- 暂停且暂不推进的任务降级为 `vault/parked.md` 条目。
- 不保存密钥。

## Recent Changes

- 替换为近期相关变化。

最多保留 10 条；更早的条目在压缩时并入任务文件执行历史。

## Known Risks

- 替换为已知风险。

## Required Checks

```bash
replace-with-project-check
```

## Next Steps

- 替换为下一步。
