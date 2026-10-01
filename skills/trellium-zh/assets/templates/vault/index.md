# Vault Index

本文件负责将 Agent 路由到正确项目上下文，并承载项目策略块。不要把它写成项目历史，也不要当作第二状态面。

<!-- trellium-policy
{
  "schema_version": 2,
  "storage_mode": "tracked",
  "budgets": {
    "runtime": {"max_lines": 120, "max_recent_entries": 10},
    "handoff": {"max_lines": 100, "max_entries": 3},
    "decisions": {"max_lines": 150, "max_records": 8},
    "parked": {"max_lines": 60, "max_entries": 20},
    "tasks": {"max_active_tasks": 40}
  }
}
-->

上方策略块是项目预算与 TASK storage 的唯一来源。`storage_mode: tracked` 表示任务文件纳入版本控制；`local` 表示任务文件、review 台账与 archive 不进 Git（Accepted 后的结论必须蒸馏进 `decisions.md` 等公开位置）；`private` 表示目标项目的全部 Trellium managed material 不进 Git，terminal TASK/review 可另存本机 History Store（由 `.git/info/exclude` 的 canonical trellium-private block 强制）。协议其他位置的预算数字是初始化默认值，不是项目当前策略。策略块缺失即 legacy 项目：如实报告，不用隐藏默认值替代。

## 任务与授权速查表

- Level C 治理任务：命中风险域即治理，一行修改也不例外（安全/隐私、公开 API/外部契约、持久数据/迁移、部署、依赖、成本/配额、架构方向、治理规则）；记 `tasks/*` 和 `decisions.md`，需用户确认。
- Level B 追踪任务：非 C 风险域但中断恢复或协作成本明显较高（跨 session、真实 handoff、多 owner、外部系统状态、多阶段 gate）；记 `tasks/*`。
- Level A 简单任务：低风险、恢复与协调成本低，默认不持久化 TASK lifecycle；仅 project-global runtime 变化时记 `runtime.md`。
- 规模（文件数、验收项数）只提示判断，不单独决定等级。
- 授权等级：0 只读 / 1 局部修改 / 2 限定范围 / 3 需确认 / 4 禁止。
- 判定模糊或涉及治理规则本身：读完整 `governance.md`。

## 文件职责

- `index.md`（本文件）：路由 + `trellium-policy` 项目策略块；不保存运行态。
- `project.md`：稳定项目目标、范围、边界和阶段。
- `runtime.md`：项目全局当前状态、可选导航 Focus、检查、风险和下一步；不拥有 TASK 状态或清单。
- `governance.md`：任务等级、授权、任务契约、验收门、升级和交接。
- `decisions.md`：长期决策索引与（未拆分前的）决策记录；正文拆分后在 `vault/decisions/D-xxxx-*.md`。
- `handoff.md`：真实中断的 transient delta；每条以任务编号命名（无任务编号用 SESSION），只含三小节（Why interrupted / Transient context not captured elsewhere / Exact resume point）；恢复时先读 TASK 与实时 Git/测试，再用 delta 补齐，消费后即删。
- `parked.md`：用户挂起事项冷索引；仅被提及时读取，不进默认读取路径。
- `collaboration.md`：不能覆盖硬规则的软协作偏好。
- `tasks/README.md`：任务文件生命周期流转、状态块规则和模板。
- `details/*`：可选长上下文，只有重复读取需要时创建。

## 细节路由

- 架构：`vault/details/architecture.md` 和 `vault/decisions.md`。
- 开发工具、依赖、测试或环境：`vault/details/development.md`。
- API 契约：`vault/details/api.md` 和 `vault/decisions.md`。
- Agent、LLM、prompt 或工具行为：`vault/details/agent.md` 和 `vault/decisions.md`。
- 领域知识：`vault/details/domain.md`。
- 协作偏好：`vault/collaboration.md`。

## 更新规则

- 热文件更新纪律：固定段落顺序，每条内容占一行；状态或进展变化用单行替换，不重写整段。
- 用户挂起任务时在 `parked.md` 记条目；重新提起时升回任务文件。
- 将长细节移出 `runtime.md`。
- local 任务（`storage_mode=local`）在 fresh clone 中缺失符合 storage contract；`runtime.md` 不承担恢复副本职责（见 governance.md）。
- 更新热文件时检查预算线；当前上限以上方 `trellium-policy` 策略块为唯一来源。
- 预算超出只在 `trellium.py check` 中呈现为健康 warning，不阻塞任务验收；压缩由显式意图（用户要求/独立 maintenance TASK/任务契约）触发：测量→分类→重组→校验→记录；语义判定（Superseded/Merged/Expired）只提案，用户确认前保持 Active。
