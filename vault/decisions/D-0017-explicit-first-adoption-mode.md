# D-0017 - 首次项目接入明确选择存储模式

Status: Active

Date: 2026-10-01

## Background

D-0012 要求首次接入询问 storage，但未指定时默认 Local，仍可能在用户没有选择 Git 可见性时写入。Owner 明确同意评估中的必答项与复用规则实施；个人习惯提问不在本次范围。

## Decision

首次给具体项目接入 Trellium 前，若 owner 未明确选择 Private/Local/Tracked，Agent 询问并等待；未回答只可只读扫描，不运行 adopt、不创建目标 TASK 契约、不写目标文件。推荐仍为 Local，预选或等待超时不算选择。

当前对话或既有授权已明确本项目模式则复用，不重复询问。既有项目保留有效 policy；缺失、无效或冲突时写入前澄清，不套默认值或自动迁移。仅安装机器级 Skill 包、目标项目未知时，问题留到首次项目接入，无全局模式。

## Compatibility

本决定替代 D-0012，保留其 Local 推荐、窄 TASK/review/archive ignore、协作核心 tracked 与模式迁移需 owner 评审的边界，仅取消未指定时的写入 fallback。三个模式、History、policy schema、CLI与默认模板内容不变；低层 adopt 仍非交互，不宣称工具自身强制此门。canonical 选择契约位于 70-adoption-flow，双语 Skill 随新包分发，2026.10.1 不改写。

## Verification

TASK-0033 以真实隔离目标的写入与 Git 边界、提问/复用行为核对该契约；关键词存在不是行为证明。是否发布新版或更新本机包另行授权。
