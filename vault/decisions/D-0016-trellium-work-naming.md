# D-0016 - 项目工作流命名 Trellium Work

Status: Active

Date: 2026-10-01

## Decision

Owner 明确同意将现有 agent-task starter workflow 更名为 trellium-work，标题 Trellium Work，目标目录 skills/trellium-work；安装/接入包 trellium / trellium-zh 保持原名。工作内容、AGENTS.md + vault 路由及发现边界不变。

## Compatibility

新项目仅生成新路径，分发模板仍使用不可发现文件名。既有项目按 MIGRATIONS 显式移动、保留定制并协调 stamp/Private exclude；未迁移项目的写入拒绝，旧配置只读检查兼容。stamp schema、History 身份/格式、storage 默认不变；不自动修改用户级 Skill。

## Relation to D-0009

D-0009 的第二项目入口/跨 Agent 发现机制 No-Go 继续有效。本决定只改变当前代码已生成的 starter workflow 的名称，不重开该架构实验，不宣称各 Agent 自动发现普通 skills/ 目录；旧实验与推理保留原文。
