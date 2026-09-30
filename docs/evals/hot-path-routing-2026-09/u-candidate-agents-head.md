执行低风险、低恢复成本的普通 Level A 任务前，读取：

1. `vault/runtime.md`
2. 与改动路径匹配的工程规范（如存在）与仓库现状

首次进入项目时读取 `vault/project.md`。

Level B 或 Level C、分级或授权判定模糊、涉及治理规则本身、已分配任务文件的续作、真实中断、需要读写 Vault/判断 storage 或预算、以及初始化/升级类工作：先读取 `vault/index.md`，再按其契约追加 governance、任务文件或必要 delta；跳读不授予任何额外权限。

修改或评审源码、公开 API、依赖、构建、并发或生命周期行为时，读取 `docs/engineering/profiles/` 下 root 与当前路径匹配的 profile；只应用当前文件实际语言的 profile，不读取未匹配语言。纯注释/文档工作——注释、Doc Comment、docstring、TODO/FIXME、directive 排布——只读 Comment/API Documentation Policy（`docs/engineering/code-comments.md`），它是该表达规范的唯一 owner。公开 API 变化，或行为与注释同时修改时，profile 与 Comment/API Documentation Policy 并读：表达规范以 Comment Policy 为准，API 行为、安全、错误与兼容性仍由完整 profile 约束。
