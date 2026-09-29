# 协议模块说明

本目录保存 `init/INIT.md` 引用的模块化 Agent 协作治理协议。

`init/INIT.md` 是入口清单；本目录中的文件是协议正文。

## 读取顺序

1. `00-overview.md`
2. `10-vault.md`
3. `15-vault-compaction.md`
4. `20-governance.md`
5. `30-agent-entry.md`
6. `40-skills.md`
7. `50-engineering-constraints.md`
8. `60-initialization-flow.md`
9. `70-adoption-flow.md`
10. `80-execution-patterns.md`
11. `90-collaboration-profile.md`

`profiles/` 下的文件是可选的项目类型 profile：

- `profiles/python-backend.md`：Python 后端默认值。
- `profiles/go-backend.md`：Go 后端默认值。

选择 profile 时，工具为每个已选语言生成完整工程规范 `docs/engineering/profiles/<profile>.md`，并保留兼容载体 `docs/engineering/code-comments.md`；工程文档不进入 Vault，`AGENTS.md` 只保留按 root 与实际语言触发的一跳路由。完整规则见 `70-adoption-flow.md`「Profile 工程规范」。

## 源文件边界

`init/` 是初始化协议源目录，其中 `init/INIT.md` 是入口清单，`init/protocol/` 是协议正文。

它们用于指导 Agent 生成或更新项目产物，包括：

- `AGENTS.md`
- `README.md`
- `vault/`
- `skills/`
- Agentic 执行模式
- 可演化协作画像
- 源码和测试文件
- 依赖配置文件

修改初始化行为时，更新 `init/INIT.md` 或 `init/protocol/`。

修改当前项目状态时，更新 `vault/`。

修改当前项目的 Agent 入口规则时，更新 `AGENTS.md`，并同步相关工具入口文件。

自包含 Skill 包是从协议源收敛出的可安装分发形态。它们面向直接安装和复用，不要求目标项目携带完整 `init/` 目录。修改核心协议设计时，应检查这些 Skill 是否仍与协议源对齐。

## 使用模式

本协议支持两种模式：

- 新项目初始化：按 `60-initialization-flow.md` 创建项目骨架和 Agent 协作层。
- 既有项目接入：按 `70-adoption-flow.md` 只安装或更新 Agent 协作层，不改业务工程层。
