---
name: trellium-work
description: 用于执行需要上下文读取、限定范围修改、验证、任务记录或 vault 记忆更新的非琐碎项目任务。
---

# Trellium Work

## Steps

1. 按 `AGENTS.md` 的入口规则读取必要上下文并判断任务等级和授权等级。
2. 按 `vault/index.md` 读取任务特定上下文。
3. 用三步判断分级：命中 Level C 风险域？→ 是即 C。否则，中断恢复或协作成本明显较高？→ 是即 B。否则 → A。规模（文件数、diff、验收项数）只提示判断，不单独决定等级；细则见 `vault/governance.md`。
4. 判断授权等级和是否需要用户确认。
5. 明确目标、范围、不做范围、验收标准和检查。
6. Level B 或 Level C 创建或更新任务文件。任务文件的 `trellium-task-state` 状态块是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner：每次状态变化只更新状态块；`runtime.md` 不保存 TASK 投影。没有状态块的旧任务文件是 legacy：下次接触时补上。
7. 做最小必要修改。
8. 行为变化时添加或更新聚焦测试。
9. 通过任务文件让长任务可恢复；仅真实中断且存在非可推导 transient delta 时写三小节 handoff（Why interrupted / Transient context not captured elsewhere / Exact resume point；恢复顺序 TASK → Git/工作区/测试 → handoff delta）。
10. 运行必要检查。
11. 检查验收门；测试通过不等于完成。
12. 多轮 review 使用 `vault/tasks/TASK-xxxx-review.md` 台账：findings 编号进入、批量处理、批量回写状态（open/fixed/wont-fix/needs-discussion）；收敛后结论归档进任务文件 Execution Record，原台账文件保留在原路径（历轮 findings 与处置的历史载体，local/private 任务 terminal 时随 TASK 成组保全）。
13. 仅在 project-global runtime 发生变化时更新 `vault/runtime.md`；需要时调整 Focus，但 Focus 只有导航语义，不拥有 task state、Authority 或活跃任务清单。
14. 长期决策写入 `vault/decisions.md`。local 或 private 任务（local lifecycle 语义）进入 `accepted` 前在任务文件 Memory Updates 填写 Durable knowledge disposition：`none — <理由>` 或 `distilled — <canonical 目标文件>`；未填写视为 `pending`，不得进入 `ready_for_review` 或 `accepted`。错误契约直接 `superseded`，不受该 gate 阻塞。
15. local/private 任务 terminal 后执行 Historical Retention：TASK 与已开展 ledger review 的相应台账成组分别写入本机 Historical Store 并逐份 get 验证，整组成功才算 retention 完成；失败保留 source、accepted 不回滚、幂等重试；默认不 cleanup，删 source 需 owner 明确授权。身份与调用路径见 trellium Skill 的 local/private 接入说明；Private 身份保持 ignored，外部 Store 不进项目 Git；tracked 不触发。
16. 用户挂起任务或决定时，在 `vault/parked.md` 记条目（含重启触发器）；用户重新提起时升回任务文件（draft）。
17. 压缩或 storage 决策前，从 `vault/index.md` 的 `trellium-policy` 策略块读取项目预算与 TASK storage；该块是当前数字的唯一来源。缺失时视为 legacy：人工判断按协议初始化默认值执行，并如实报告缺口。
18. 任一热文件超出预算线时，如实报告 `BUDGET_EXCEEDED` warning（仓库健康信号），不阻塞当前任务验收、不自动扩大本任务 scope；仅当用户显式要求、独立 maintenance TASK 或本任务验收标准明确包含压缩，或热文件结构损坏需要恢复时，才执行压缩五阶段：测量→分类→重组→校验→记录。压缩规则：
    - decisions 索引化与任务归档是零信息损失的搬运，可自主执行。
    - 暂停任务降级为 `parked.md` 条目是搬运，可自主执行；parked 清理只出提案。
    - Superseded/Merged/Expired 判定只出提案清单，用户确认前一律保持 Active。
    - 压缩前 `vault/` 必须无未提交变更；压缩形成只含 `vault/` 变更的独立提交；校验失败即恢复。
19. 本次任务中出现用户协作偏好或纠正信号时，按观察记入 `vault/collaboration.md`；重复出现或用户确认后升为偏好。

## Constraints

- 不引入无关依赖或框架。
- 不保存密钥。
- 单元测试不依赖真实外部服务。
- 不静默覆盖用户改动。
- 涉及架构、公开 API、数据模型、安全、隐私、成本、部署、依赖或 Agent 治理时升级。

## Review Before Completion

- 逐条确认验收标准。
- 确认验证输出。
- 确认 vault 记忆已更新。
- 确认没有隐藏高影响变更。
