# 协议模块说明

本目录保存 `init/INIT.md` 引用的模块化 Agent 协作治理协议。

`init/INIT.md` 是入口清单；本目录中的文件是协议正文。

## 读取顺序

1. `00-overview.md`
2. `10-vault.md`
3. `20-governance.md`
4. `30-agent-entry.md`
5. `40-skills.md`
6. `50-engineering-constraints.md`
7. `60-initialization-flow.md`
8. `70-adoption-flow.md`

`profiles/` 下的文件是可选的项目类型 profile。

## 源文件边界

`init/` 是初始化协议源目录，其中 `init/INIT.md` 是入口清单，`init/protocol/` 是协议正文。

它们用于指导 Agent 生成或更新项目产物，包括：

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `vault/`
- `skills/`
- 源码和测试文件
- 依赖配置文件

修改初始化行为时，更新 `init/INIT.md` 或 `init/protocol/`。

修改当前项目状态时，更新 `vault/`。

修改当前项目的 Agent 入口规则时，更新 `AGENTS.md`，并同步相关工具入口文件。

当前不抽取 `templates/`。当协议稳定并需要跨多个项目重复初始化时，再考虑将生成物模板独立出来。

## 使用模式

本协议支持两种模式：

- 新项目初始化：按 `60-initialization-flow.md` 创建项目骨架和 Agent 协作层。
- 既有项目接入：按 `70-adoption-flow.md` 只安装或更新 Agent 协作层，不改业务工程层。
