# Handoff

真实中断的 transient delta 专用：仅当「真实中断」且「存在无法从 canonical 状态（TASK、Git、工作区、重跑测试、durable knowledge）低成本推导的恢复事实」同时成立时写入。正常完成、等待 acceptance、普通 review、open lifecycle 或可推导的干净会话边界不产生条目。

每条以任务编号命名（无任务编号时用 SESSION），只含三小节：`### Why interrupted`（为何在当前上下文停下）、`### Transient context not captured elsewhere`（无法重现的现场）、`### Exact resume point`（精确续作动作）。恢复顺序：TASK 文件 → 实时 Git/工作区/重跑测试 → handoff delta；delta 消费后删除该条目，durable 结论必须已在 canonical 位置。

不把实时 Git 状态当权威记录；累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。
