# 00 - 概览

## 定位

本协议用于初始化适合长期 AI 协作开发的 Agent-Native 项目。

它不是业务规格说明，也不是单一工具配置文件。它是以下内容的源协议：

- Agent 入口文件；
- vault 项目记忆系统；
- Agent 协作治理；
- 任务契约和验收门；
- 可复用 Agent skills；
- profile 相关的工程结构。

## 核心原则

Agent 不按身份获得信任，而是按任务契约获得授权，并按验收标准关闭任务。

## 设计分层

- 入口层：`AGENTS.md`、`CLAUDE.md` 或其他工具入口文件。
- 上下文层：`vault/index.md`、`vault/project.md`、`vault/runtime.md` 和 `vault/details/*`。
- 治理层：`vault/governance.md` 和 `vault/tasks/*`。
- 决策层：`vault/decisions.md`。
- 接力层：`vault/handoff.md`。
- 工作流层：`skills/*/SKILL.md`。
- Profile 层：语言或框架相关的项目默认值。

## 非目标

- 核心协议不强制绑定某种编程语言。
- 不把项目百科塞进入口文件。
- 不把所有历史事件都塞进 `runtime.md`。
- 不用固定角色层级来表达多 Agent 协作。
- 在项目类型真正需要之前，不引入框架、数据库、LLM SDK、部署或 CI 选择。
