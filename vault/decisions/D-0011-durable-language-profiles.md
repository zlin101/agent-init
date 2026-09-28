# D-0011 - 完整语言 Profile 的项目级持久化（2026-09-18）

Status: Active

## Background

TASK-0012 只把注释/API 规则持久化到项目；`init/protocol/profiles/go-backend.md` 的 module/workspace、分层、依赖、错误、资源、并发、HTTP、测试等完整工程知识仍只在首次控制 Skill 会话可见，后续普通会话会遗忘。Owner 明确裁定持久化能力必须交付，只消融载体。

## Decision

每个显式选择的 profile 生成独立完整项目文档 `docs/engineering/profiles/<profile>.md`，内嵌该 profile 的 roots；`AGENTS.md` 对工程任务一跳按当前路径与实际语言读取，不加载未匹配 profile。文件进入 adoption stamp 的 core 和 upgrade/diff 管理，profile metadata 记录 roots、完整源 hash、兼容注释规则路径与 `project_profile`。不自动猜语言，不写 Vault，不自动 Git add/commit/push。

中文发行模板由 canonical `init/protocol/profiles/*.md` 机械派生并做 byte-equality 防漂移；英文发行模板是同覆盖面的本地化派生，并由九类覆盖与真实 embedded-package adopt 测试约束。既有 `docs/engineering/code-comments.md` 作为 2026.09.7 兼容载体继续保留：迁移不删除、不覆盖定制，双方变化只出 proposal。

## Rationale

冻结消融要求压缩 capsule 先证明九类语义无损；当前没有该证据，因此 R1 淘汰并选择完整 profile。每语言一文件让多 root 共享同语言规则，同时防止多语言正文混用；把 12KB+ 工程规范放在条件路由目标而非默认 AGENTS/Vault，以文件复杂度换取按需 token。

## Impact

2026.09.8 的 legacy v2 profile 项目在 `upgrade --apply` 时新增完整 profile 文件；pristine 跟进上游，定制冲突走 proposal。未选 profile 输出集合不变。新增 profile 文件属于协作 core，必须进入 Git HEAD，fresh clone checker 才能通过。
