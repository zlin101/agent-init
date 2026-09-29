# Kill Gate 1 探针 prompt（逐字）

两个 agent 使用完全相同的中性 prompt；不出现 `AGENTS.md`、`exclude`、`ignored` 等提示词，发现入口文件本身即是测试目标。

```text
按本项目的协作规则回答：执行任何非琐碎任务前，你必须读取哪些文件？逐项列出，并按项目要求提供验证标记。
```

判定所需的 sentinel 由 fixture 中的 `AGENTS.md` 提供（`PRIVATE-DISCOVERY-SENTINEL-7QF3`）；agent 只有真实读取该文件才可能引用它。
