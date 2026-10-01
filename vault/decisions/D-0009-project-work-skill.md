# D-0009 - 项目工作 Skill 方向关闭（2026-09-18）

Status: Active

## Background

TASK-0011 按预注册 A0/A1 消融（三场景 × 两臂 × 独立首答）验证项目级工作 Skill：两臂全场景 0 关键遗漏 / 0 需要纠正 / 0 硬指标违规（A0 的 AGENTS.md+vault 底座充分，地板效应），A1 成本更高；结构测试证实 Codex 不发现项目级 `.claude/skills/` 且其全局 `agent-task` 泄漏源自机器级控制包安装。owner 验收 No-Go 并关闭方向。

## Decision

项目级工作 Skill（trellium-work）不实现；`AGENTS.md + vault` 为既有项目接入的标准底座，Claude Code 直接读取 `AGENTS.md`，不再生成独立 `CLAUDE.md`；控制面保持用户级 `trellium`/`trellium-zh`；控制包模板源以不可发现文件名分发（AGENT_TASK_SKILL.template）。未来重开需 owner Level C 立项且以新的实证为准。

## Rationale

入口路由层不是 reviewer 深度的瓶颈；跨 Agent 的项目级发现位置缺乏可验证的一致机制。

## Impact

新项目接入只产出 AGENTS.md+vault，不为 Claude Code 复制第二份项目入口；不安装第二项目 Skill；`agent-task` 名称不再以可发现形态存在于发行包。

2026-10-01 限定说明：D-0016 将已存在的 starter workflow 改名为 trellium-work；不新增第二入口或跨 Agent 自动发现机制。本决定及原实验结论保持有效，历史名称不回溯改写。
