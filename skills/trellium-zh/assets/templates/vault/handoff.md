# Handoff

仅当真实中断留下无法从 canonical 状态低成本推导的恢复事实时，才写入 transient delta。仅当两条同时成立时才写入条目：发生了真实中断（完成前的会话边界、Agent 所有权切换、owner 暂停、环境或外部依赖不可用、不可重现的半完成瞬态操作），且至少一条恢复事实无法从 canonical 状态（TASK 文件、Git、工作区、重跑测试、durable knowledge）低成本推导。正常完成、等待 acceptance、已完成 review、单纯 open lifecycle、普通下一步或完全可推导的干净会话边界不产生条目。

每条以任务编号命名（无任务编号时用 SESSION），只含三小节：

- Why interrupted：为什么在当前上下文停下。
- Transient context not captured elsewhere：无法重现的现场。
- Exact resume point：精确续作动作，仅在超出任务 slice 导航价值时写。

恢复顺序：先读 TASK 文件、实时 Git/工作区并重跑测试，再用 handoff 条目补 transient delta，消费后删除该条目；durable 结论必须已在 canonical 文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取，不作为本文件的权威状态。

local 任务（`task_storage=local`）关闭后，删除本文件中与其相关的 transient delta；稳定结论先落入 canonical 文件。
