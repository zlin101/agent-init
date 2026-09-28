# D-0006 - Local TASK 私有边界与 clone-safe 投影（2026-09-09）

Status: Active

## Background

local TASK 设计上就是 ignored 的私有工作日志（不进仓库、可丢弃），但 09.3 的 checker 把 fresh clone 中 runtime 指向的 missing local TASK 判成与 tracked 丢失相同的 error，没有表达"按策略不可见"与"真丢失"的区别；且 local 任务进入 accepted 前没有显式的长期知识处置检查点。

## Decision

local TASK 保持私有、临时、低仓库负担：任务关闭前把会约束未来实现的最小结论蒸馏到 canonical 文件（decisions/project/details/公开契约），没有则记录 `none`；蒸馏是人工 review gate，不做自动提取。runtime 中 missing open local TASK 产生 clone-safe warning，明确"可能是正常 fresh clone 也可能误删"，并声明 runtime 摘要不授予任何 Authority——继续任务必须取回原任务文件或经 owner 批准重建契约。closed local TASK 不得留在 runtime 热路径。tracked 模式的全部严格校验保持不变。

## Rationale

local TASK 的价值在于私有和低负担；把它重新包装成需要发布的资产会制造重复事实源。机器无法判断"什么值得长期保留"，这是人工判断；机器能做的是把证据边界表达清楚并 fail closed。

## Alternatives

- 自动发布/归档 local TASK 或 publish generator：被否，制造第二事实源。
- 把 missing local 静默忽略：被否，无法区分正常 fresh clone 与误删，且会诱导 Agent 从 runtime 摘要恢复越权工作。

## Impact

Agent 遇到 missing local TASK 的 runtime 行时：不据此获得授权、不重建契约，先向 owner 取回原文件或申请重建。`2026.09.4` 起新关闭的 local 任务需人工完成 Durable Knowledge Disposition；历史任务不批量回填。tracked 项目行为零变化。
