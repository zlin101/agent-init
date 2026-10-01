# Decisions

长期决策索引。当前任务进展放 `vault/runtime.md` 或 `vault/tasks/*`；每条决策正文位于 `vault/decisions/D-xxxx-*.md`。

每条决策标注状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。默认 `Active`。

## 决策索引

- D-0001 · Canonical K1-K4 实验契约 · Active · shadow 观测以 2026-09-04 计划第 2 节为唯一定义，旧标签映射为 A1/A2/canonical K2，历史不改写 · 2026-09-08 · 正文见 `vault/decisions/D-0001-canonical-k1-k4.md`
- D-0002 · Self-hosting vault check 进入 CI 门禁 · Active · PR 与 main/develop push 运行只读 check；写权限仅限 PR self-heal job，push 任务严格只读 · 2026-09-08 · 正文见 `vault/decisions/D-0002-self-hosting-ci-gate.md`
- D-0003 · Release 元数据降为可选改进 · Superseded by D-0013 · 历史版本曾要求 GitHub Release；2026-09-28 起 Trellium 改为只发布 tag · 2026-09-08 · 正文见 `vault/decisions/D-0003-release-metadata-optional.md`
- D-0004 · Context 功能 No-Go · Active · M4/`trellium.py context` 未授权不实现；AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件 · 2026-09-08 · 正文见 `vault/decisions/D-0004-context-no-go.md`
- D-0005 · 覆盖计数单源 · Active · 覆盖事件以 shadow ledger append-only 行为唯一事实源；数字汇总仅为 dated derived snapshot；runtime/handoff 只引用不维护副本 · 2026-09-08 · 正文见 `vault/decisions/D-0005-coverage-single-source.md`
- D-0006 · Local TASK 私有边界 · Superseded by D-0014 · 曾定义 local TASK 为私有可丢弃日志；2026-09-30 起仓库负担目标与蒸馏 gate 仍有效，disposable 推导废止，local terminal 证据按 D-0014 成组保全 · 2026-09-09 · 正文见 `vault/decisions/D-0006-local-task-boundary.md`
- D-0007 · 只读 status 摘要命令 · Active · `trellium.py status`（text/JSON v1）编译 check 已校验的状态层；closed 只计数，unresolved fail-closed，不扩 schema、不是 approval inbox · 2026-09-09 · 正文见 `vault/decisions/D-0007-read-only-status.md`
- D-0008 · Review Pack 方向结论与 R2 处置 · Active · R1 为 Inconclusive；R2 本周期不实现、不提案，重开需 owner 另立 Level C 任务 · 2026-09-13 · 正文见 `vault/decisions/D-0008-review-pack.md`
- D-0009 · 项目工作 Skill 方向关闭 · Active · `trellium-work` No-Go；AGENTS.md + vault 为项目底座，控制面保持用户级 Skill · 2026-09-18 · 正文见 `vault/decisions/D-0009-project-work-skill.md`
- D-0010 · Git 接入持久性 Gate · Active · checker 对协作核心的 HEAD、ignore 与 local 边界 fail-closed；不自动执行 Git 写操作 · 2026-09-18 · 正文见 `vault/decisions/D-0010-git-durability-gate.md`
- D-0011 · 完整语言 Profile 的项目级持久化 · Active · 显式选择的完整 profile 进入项目 core 和 upgrade/diff 管理，不自动猜语言 · 2026-09-18 · 正文见 `vault/decisions/D-0011-durable-language-profiles.md`
- D-0012 · 首次接入默认 local TASK storage · Active · Skill/Agent 先询问并推荐 local，未指定时按 local 执行；只有 TASK/review/archive 留在本地，核心仍 tracked；不新增 CLI API，存量策略不自动迁移 · 2026-09-28 · 正文见 `vault/decisions/D-0012-local-default-task-storage.md`
- D-0013 · Trellium 静默发布仅推送 tag · Active · 后续版本不创建 GitHub Release，也不生成 release 文本；`--fetch` 与显式 `install.sh --version` 已支持 tag；未指定版本的安装已改为 fail-closed（TASK-0024 移除 latest-release 解析） · 2026-09-28 · 正文见 `vault/decisions/D-0013-tag-only-releases.md`
- D-0014 · Local Historical Evidence Store · Active · local 描述仓库可见性而非保留策略：terminal local TASK/review 经本机 Store 成组保全并可按项目/逻辑身份找回核验；身份唯一 owner 为 tracked `vault/project-id`；disposition 与 retention 正交；历史不授予 Authority · 2026-09-30 · 正文见 `vault/decisions/D-0014-local-historical-evidence-store.md`
