# Shadow Run 观测记录 — 2026-09

预注册的 K1-K4 实验观测。规则：只记录事实事件，不写感受；指标与成功标准一经写入不再修改；每条观测带日期与触发事件。试点任务见 `vault/tasks/TASK-0001-self-hosting-pilot.md`。

## Experiment contract reconciliation（2026-09-08，TASK-0003 M1）

本块按 `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` 第 6 节追加。初版 ledger 使用的 K1-K4 标签与 2026-09-04 实施计划第 2 节预注册的 canonical 假设存在同名异义；自本日起以 canonical 定义为准。以下既有表格与观测行原样保留，不删除、不改写；各节标题保留初版标签作为历史出处。

| Canonical | 定义（2026-09-04 计划第 2 节） | 初版 ledger 对应 | 处置 |
| --- | --- | --- | --- |
| K1 | 状态块确实比纯 Markdown 更少漂移 | 初版 K1（同名同义） | 继续在初版 K1 表追加新观测 |
| K2 | 项目级 tracked/local 策略足够表达现实 | 初版 K3（同名异义） | 初版 K3 表即 canonical K2 观测表；标题保留历史原样 |
| K3 | 不解析任意 Markdown 也能产生高价值检查 | 初版缺失 | 用本块下方新建表，自 2026-09-08 起采集，不回填 |
| K4 | checker 应先于 context compiler | 初版缺失 | 用本块下方新建表，自 2026-09-08 起采集，不回填 |
| A1（辅助） | runtime 投影值得保留 | 初版 K2（同名异义） | 降为辅助指标 A1；初版 K2 表继续记录，不冒充 canonical K2 |
| A2（辅助） | 预算测量确有价值 | 初版 K4（同名异义） | 降为辅助指标 A2；初版 K4 表继续记录，不冒充 canonical K4 |

覆盖计数核对（**derived snapshot，截至 2026-09-28（TASK-0016 active；TASK-0013/0014/0015 accepted），审计基准（固定锚点）：TASK-0006 的 rfr 提交为 `bf3f84b`（2026-09-08）、TASK-0007 的 rfr 提交为 `430de35`（2026-09-09）、TASK-0011 的 rfr 提交为 `aa8038e`（2026-09-16）、TASK-0012 的实现提交为 `bbae794`（2026-09-16）、TASK-0013 的修复提交为 `bcbc480`（2026-09-18）、TASK-0013/0014/0015 的合并实现提交为 `7582e7c`（2026-09-20）；对账补记提交为 `703b140`**；事实源为本文件下方 append-only lifecycle 事件行与实际任务文件，本段仅为派生汇总，不得在他处复制维护——D-0005）：真实 TASK 共 16 个（TASK-0001…0016；review ledger 非 TASK 实体）。计数规则：有 owner 立项且非演示交付的 Level B/C 任务计入；纯演示、纯为实验构造的 TASK 与一切 synthetic 实验样本不计入；TASK-0014/0015/0016 由 owner 直接创建为 active，没有发生创建转换；TASK-0013 初建 draft，2026-09-18 接手实施时 draft→active（见事件行）。观测到 lifecycle 转换 40 次（TASK-0016 直接创建为 active，不新增转换；历史明细保留在下方 K1 append-only 事件行），blocked→active 2 次。handoff 现存条目数 ≠ 历史跨 Agent handoff 次数；**已完成的跨 Agent handoff 事件 2 次，均有交接前 check 留档**。TASK-0001 的 coverage gate（5 TASK / 6 转换 / 2 handoff / 1 blocked→active）已达到，但不替代 canonical K1-K4 的跨项目证据要求。

### Canonical K3 — 不解析任意 Markdown 也能产生高价值检查（2026-09-08 起）

两个真实 Vault 只读运行；记录 finding 是否对应真实修复，以及已知遗漏。

| 日期 | Vault | 触发 | errors / warnings | 是否产生真实修复 | 已知遗漏 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-08 | trellium（本仓库） | TASK-0003 M1 校准后 check | 0 / 1 | 否：预期瞬态 finding（tracked 任务未提交窗口，设计内行为），随例行提交消除，不构成缺陷捕获证据 | 暂无 | review round 1 更正定性（原行误标为"真实修复"）；canonical K3 尚无缺陷捕获类观测 |
| 2026-09-08 | trellium（本仓库） | 交接复核发现计数不一致（runtime/ledger 写 3 TASK，checker 报 current_task_files=4） | 0 / 0 | 是：人工核对后更新 runtime 与 ledger 计数；checker 未参与发现 | checker 不解析自然语言统计数字，prose 计数过期不可见 | 真实遗漏样本，佐证 K3 边界；同时是跨文档计数漂移的候选证据（单次，不自动触发 Phase 2 准入） |
| 2026-09-18 | orion（第二真实项目） | accepted local TASK-0001 收尾检查 | 1 / 0 | 是（待执行）：删除关闭任务的 runtime 行并清理 Focus | 不验证安装 stamp、核心协作层是否 tracked，也不解析自然语言 AC 勾选状态 | `TASK_RUNTIME_CLOSED_LOCAL` 精确对应真实修复；这是 canonical K3 首条跨项目高价值 finding，修复完成前不记为 closed |

成功标准：finding 对应真实修复动作。Kill criterion：连续两次真实检查只有无行动价值的 warning，且遗漏已知的状态/storage/预算错误。

### Canonical K4 — checker 应先于 context compiler（2026-09-08 起）

记录 checker 发现数、状态判断耗时、owner 手工打开文件数与上下文选择成本。

| 日期 | 事件 | checker 发现数 | 状态判断耗时 | owner 打开文件数 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-08 | GitHub Actions 首跑（develop push，gate job） | 0 | n/a（CI 自动执行） | 0 | run 34181086563：self-hosting check 首次在 runner 执行，0 finding，job success |
| 2026-09-08 | 冷启动基线 S1-S7（各独立新会话，详见 cold-start-baseline-2026-09.md） | n/a | 每场景读取 5-16 个文件，bytes/耗时大部分未采集 | 0（owner 仅记录，未打开文件代答） | 判断 7/7 正确、0 越权、0 过期证据误用；上下文选择成本有界但可见——K4 kill criterion 的首轮量化输入 |
| 2026-09-09 | TASK-0008 status 五问盲测（3 个无历史会话各只看一份手写 S1 输出） | n/a | 每会话仅凭 S1 输出回答五问，未打开任何 runtime/TASK 文件；3/3 场景首答全对、0 纠正 | 0 | S1 文本 1149 bytes < runtime.md 11039 bytes；bytes 仅 guardrail，未做 owner 可用性复核，不声称时间节省 |
| 2026-09-09 | TASK-0008 S0 臂补齐（owner review 后）：3 个无历史会话各看现行流程材料（runtime 全文 + 全部状态块）回答同五问 | n/a | 场景 1 全对；场景 2 closed 计数需材料未定义的推断；场景 3 把缺失文件任务的 Next Action 记录过度声称可用（1 次纠正） | 0（材料为全文输入，无后续打开） | 双臂逐字首答与评分存 `vault/details/status-blind-test-2026-09.md`；S1 差异点：open/closed 分类学内建 + fail-closed 投影抑制 |
| 2026-09-18 | Orion 真实 Level C local 任务复核 | 1 | 未采集 | n/a（审计读取，未计量） | Agent 通过 AGENTS→vault 完成任务并写 Durable Disposition，说明现行路由可用；成本未测且 check 有真实 finding，不触发 D-0004 的 Context 重开条件 |

Kill criterion：状态准确率已接近 100%，checker 零有效发现，但上下文读取成本仍明显高；达到时重新评估最小 context manifest，不继续扩 checker。

## 基线（2026-09-04）

- 协议版本 2026.09.3；check 基线：0 error / 0 warning。
- 试点前状态：所有任务状态散落在 prose（本仓库此前无任务文件，基线为"纯 prose 时代"）。

## K1 — 状态块减少事实漂移

对比对象：历史 prose TASK（其他项目的使用经验与本仓库既往会话记录）vs 本试点的结构化 TASK。

| 日期 | 事件 | 涉及 TASK | 修改位置数 | 状态冲突/人工修正 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-04 | draft → active（接入完成） | TASK-0001 | 2（状态块 + runtime 行） | 0 | 首次转换 |
| 2026-09-04 | active → blocked（发布客户端不可用） | TASK-0002 | 2（状态块 + runtime 行） | 0 | Release 未创建，不将失败误记为成功 |
| 2026-09-08 | draft → active（M0 preflight 通过） | TASK-0003 | 2（状态块 + runtime 行） | 0 | canonical K1 校准后首个转换 |
| 2026-09-08 | active → ready_for_review（M1-M3 实施与验证完成） | TASK-0003 | 2（状态块 + runtime 行） | 0 | 首轮记录遗漏本转换，review round 1 补记 |
| 2026-09-08 | ready_for_review → accepted（round 2 通过 + CI 首跑全绿，owner 授权） | TASK-0003 | 2（状态块 + runtime 行） | 0 | 两个 review round，1 次返工 |
| 2026-09-08 | blocked → active（2026.09.3 Release 已发布并成为 latest） | TASK-0002 | 2（状态块 + runtime 行） | 0 | blocker 解除；Release 标题和 notes 仍为空，未进入 ready_for_review |
| 2026-09-08 | active → accepted（owner 决定元数据 Gate 降为可选，D-0003） | TASK-0002 | 2（状态块 + runtime 行） | 0 | 技术验收项全部达成；标题/notes 移入 Optional |
| 2026-09-08 | active → blocked（M3 No-Go 采纳为 D-0004；M2 等待 owner 第二项目） | TASK-0004 | 2（状态块 + runtime 行） | 0 | 首例因等待外部输入主动转 blocked；恢复时的 blocked → active 将计入 TASK-0001 coverage gate 样本 |
| 2026-09-08 | draft → active（owner 任务书立项：证据质量与计数收敛） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 真实治理修复任务，非为凑 TASK-0001 数量门槛（D-0005） |
| 2026-09-08 | active → ready_for_review（M1 计数单源化 + M2 Protocol v2 完成） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 待 owner 最终验收 |
| 2026-09-08 | draft → active（owner 下发非 Context 优化计划开始指令） | TASK-0006 | 2（状态块 + runtime 行） | 0 | Level C 消融实验任务；实验样本 synthetic，不计入本试点覆盖 |
| 2026-09-09 | ready_for_review → accepted（owner 复核 6a2043e 通过，正式验收） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 六项 round-2 finding 已闭合 |
| 2026-09-08 | active → ready_for_review（M0-M2 消融完成，即提交 bf3f84b；**owner review 2026-09-16 对账补记**——该转换发生时未记录事件行） | TASK-0006 | 2（状态块 + runtime 行） | 0 |
| 2026-09-09 | ready_for_review → accepted（owner 验收，结论严格限定：E2 No-Go / E1 Inconclusive / v0 本周期不实现） | TASK-0006 | 2（状态块 + runtime 行） | 0 | 方向未证伪；其余候选等待真实证据 |
| 2026-09-09 | active → ready_for_review（2026.09.4 实现完成；**owner review 2026-09-16 对账补记**——该转换发生时未记录事件行） | TASK-0007 | 2（状态块 + runtime 行） | 0 |
| 2026-09-09 | ready_for_review → accepted（owner 验收通过；2026.09.4 实现闭环） | TASK-0007 | 2（状态块 + runtime 行） | 0 | tag 随验收推送；Release 对象由 owner 创建（D-0003：元数据可选） |
| 2026-09-09 | active → ready_for_review（2026.09.5 status 实现与独立 review 闭合） | TASK-0008 | 2（状态块 + runtime 行） | 0 | 实现前手写盲测 3/3 零纠正；review round 1 唯一 P1 已修复；owner 验收前不代做 tag/Release |
| 2026-09-09 | ready_for_review → accepted（owner 最终审查 APPROVE、无 open P0/P1/P2，正式验收并授权发布） | TASK-0008 | 2（状态块 + runtime 行） | 0 | durable decision 记为 D-0007；`2026.09.5` tag 指向 accepted 提交，Release 按授权顺序随后创建（无 gh 时由 owner 创建，D-0003 元数据可选） |
| 2026-09-12 | active → ready_for_review（M0-M5 完成；独立 review Round 1 REQUEST_CHANGES 修复后 Round 2 APPROVE） | TASK-0009 | 2（状态块 + runtime 行） | 0 | R1 判定 No-Go；control_invalidated 双登记待 owner 裁决；不代 owner accepted |
| 2026-09-13 | ready_for_review → accepted（owner 两轮 review 修正闭合后验收；结论锁定 Inconclusive / R2 不实现 / 12c-7v / 不得恢复 No-Go 表述，D-0008） | TASK-0009 | 2（状态块 + runtime 行） | 0 | 方案 B 历史脱敏获批执行；TASK-0010 批准排期（CI 绿后 draft→active） |
| 2026-09-13 | draft → active（方案 B 完成、push 成功、远端 CI 全绿，owner 排期生效） | TASK-0010 | 2（状态块 + runtime 行） | 0 | 范围严格限三个已裁定 status 缺陷（P1/P1/P2）；不夹带 Review Pack/Context |
| 2026-09-14 | active → ready_for_review（三缺陷修复 + red-first 测试 + 独立复审 APPROVE + 远端 CI 全绿） | TASK-0010 | 2（状态块 + runtime 行） | 0 | 中途 71c64b3 被远端 gate 以 snapshot 漂移拦截（本地管道遮蔽退出码），regen 后修复 |
| 2026-09-15 | ready_for_review → accepted（owner 验收：Focus/记录一致性修正闭合，远端 gate run 34927880245 success） | TASK-0010 | 2（状态块 + runtime 行） | 0 | 落实 D-0007 既有 status 契约，不新增决策；MIGRATIONS Unreleased 节位于 09.5 tag 之后，不改动既有 tag |
| 2026-09-16 | active → ready_for_review（A0/A1 消融 No-Go 判定落地 + 泄漏修复 + 隐私历史重写；**owner 复核发现遗漏后补记**——转换实际发生于远端 CI run success 后，投影文字曾过早声称 rfr，且本行初稿误混入 TASK-0010 内容，已更正） | TASK-0011 | 2（状态块 + runtime 行） | 1 | 修复完成、CI 绿后按正确顺序转换；此前该行曾与撤销注记混写，本轮重写为纯事件行 |
| 2026-09-18 | ready_for_review → accepted（owner 最终验收通过；隐私历史重写与泄漏修复均经 CI 绿确认） | TASK-0011 | 2（状态块 + runtime 行） | 0 | 项目 Skill 方向正式关闭（D-0009）；归档与备份引用待 owner 验收后处置 |
| 2026-09-16 | active → ready_for_review（R1 路由消融通过；2026.09.7 profile-aware 注释规范实现与结构化 review 闭合） | TASK-0012 | 2（状态块 + runtime 行） | 0 | 实现锚点 `bbae794`；136 tests、check 0/0、snapshot/whitespace 通过；待 owner accepted，不代发 |
| 2026-09-16 | ready_for_review → accepted（owner 确认已 push，并明确指示 Codex 自行验收） | TASK-0012 | 2（状态块 + runtime 行） | 0 | 本地提交后终验 136 tests、check 0/0、status 0 unresolved；远端实时查询因平台容量未返回，不伪造 CI 证据；tag/Release 另行决定 |
| 2026-09-18 | blocked → active（owner 提供 Orion 作为第二真实 local 项目并批准恢复 M2） | TASK-0004 | 2（状态块 + runtime 行） | 0 | Orion 首条观测为 Partial：checker 有 1 个真实 finding，tracked durable boundary 尚待闭合 |
| 2026-09-18 | draft → active（GLM/Claude 接手实施；M0 预注册与红测先于任何 scripts/init/skills 产品修改） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 预注册冻结于 `docs/evals/adoption-durability-2026-09/`；红测 6 格先红（含非 Git `CORE_STORAGE_UNVERIFIED` warning 契约），唯一即时绿格为 committed+dirty 控制 |
| 2026-09-19 | active → ready_for_review（owner findings 全部闭合，提交态快照 check 0/0，独立 review 无 open P0/P1/P2） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 共享工作区 2 errors 属 owner 排除文件，不冒充产品回归；无 push/tag/release |
| 2026-09-19 | ready_for_review → accepted（owner 指令“修复然后验收”） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 版本与发布仍为独立动作 |
| 2026-09-19 | active → ready_for_review（完整 profile 持久化实现与 Round 1 findings 闭合；164 tests） | TASK-0014 | 2（状态块 + runtime 行） | 0 | 预注册/实现同属未提交变更集，无 Git DAG 时序证明 |
| 2026-09-19 | accepted → active（独立增量 review 复现 HEAD marker fail-open 与发布级 fallback 路径安全问题） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 原 accepted 结论撤回，红测修复与复审前禁止发布 |
| 2026-09-19 | ready_for_review → active（增量 review 复现 legacy profile symlink 外部读取，locale 启发式需移除） | TASK-0014 | 2（状态块 + runtime 行） | 0 | 原 APPROVE 结论撤回，待修复与独立复审 |
| 2026-09-20 | active → ready_for_review（HEAD marker、精确 managed-file 集合与统一 fallback 安全边界终验通过；177 tests） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 无 open P0/P1/P2；owner accepted 与发布动作仍独立 |
| 2026-09-20 | active → ready_for_review（显式 locale、legacy link 拒绝与 selected-profile-only 授权终验通过；177 tests） | TASK-0014 | 2（状态块 + runtime 行） | 0 | tracked 任务尚未提交，accepted gate 保持打开 |
| 2026-09-20 | active → ready_for_review（Claude Code 项目入口统一为 AGENTS.md；11 tests、snapshot/whitespace 通过） | TASK-0015 | 2（状态块 + runtime 行） | 0 | 仓库与 HEAD 原本无 CLAUDE.md 实体；仅移除现行协议约定，保留 Skill 安装支持 |
| 2026-09-20 | ready_for_review → accepted（owner 确认验收无问题并授权 push） | TASK-0013 | 2（状态块 + runtime 行） | 0 | 第二轮安全修复已提交为 `7582e7c`；tag/Release 独立 |
| 2026-09-20 | ready_for_review → accepted（tracked task 与实现提交后 owner 验收） | TASK-0014 | 2（状态块 + runtime 行） | 0 | 存储前置门已由 `7582e7c` 满足；tag/Release 独立 |
| 2026-09-20 | ready_for_review → accepted（owner 确认 AGENTS.md 入口统一验收无问题） | TASK-0015 | 2（状态块 + runtime 行） | 0 | 实现提交 `7582e7c`；保留 Claude Code Skill 安装支持 |

成功标准：不再出现静默状态冲突；每个 TASK 人工修正不超过 1 次。

## K2 — runtime 投影值得保留

| 日期 | 事件 | 单次同步耗时 | check 捕获的相关发现 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | 初始建行（TASK-0001 active） | < 30 秒 | 无（人工同步正确） | |
| 2026-09-04 | TASK-0002 active → blocked | 未单独计时 | 无（人工同步正确） | 本行不计入耗时成功样本 |
| 2026-09-08 | TASK-0002 blocked → active | 未单独计时 | 无（人工同步正确） | Release/latest 核验后同步状态块与 runtime；元数据 Gate 仍未通过 |
| 2026-09-08 | TASK-0002 active → accepted 投影同步 | 未单独计时 | 无（人工同步正确） | owner 元数据决定（D-0003）后关闭任务；handoff 条目并入任务文件 |

成功标准：单次投影更新不超过 30 秒；不出现长期双写负担（若连续两次记录"忘了同步、靠 check 抓回"，即为负担信号）。

## K3 — tracked/local 足够表达存储策略

Trellium 本仓库 = tracked 样本；另一个真实私有项目 = local 样本（由用户择机接入）。

| 日期 | 项目 | 模式 | 事件 | 误提交/误忽略/例外 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-04 | trellium | tracked | `.gitignore` 白名单解除 vault/ 与 AGENTS.md；任务文件入库 | 0 / 0 / 0 | 无需第三种模式 |
| 2026-09-18 | orion | local | 真实 Level C TASK-0001 已 accepted，并声明将 Durable Knowledge Disposition 发布到 decisions | 0 / 1（核心层） / 1（待收尾） | local TASK 本身未误提交；但 AGENTS/vault/skills/工程文档整体仍未跟踪且 stamp 缺失，故 canonical K2 仅 Partial，不判通过 |

成功标准：零误提交、零模糊归属、不需要 tracked/local 之外的第三种模式或逐任务例外。

## K4 — 预算阈值确有价值

第一阶段只测量、不设阈值（policy 不配 budgets 数字）。记录热文件增长与实际阅读障碍。

设置校正：adopt 生成的默认 policy 曾短暂包含 budgets；在第二个真实任务开始、尚未产生任何阈值 finding 前删除，使实验与预注册的 measurement-only 条件一致。

| 日期 | 文件 | lines / bytes / max_line_bytes | 实际阅读障碍事件 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | runtime | 58 / 1751 / 136 | 无 | 基线 |
| 2026-09-04 | runtime | 59 / 2364 / 179 | 无 | 删除 budgets 后 check 仍报告测量，不执行阈值判定 |

判定规则：只有观察到"大文件确实导致 Agent 定位失败"的具体事件，才为对应文件配置阈值。

## check 运行台账

每次 `check --format json` 的结论留档（交接与合并前必跑）。

| 日期 | 触发 | 退出码 | errors / warnings | 发现与处置 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | adopt 后基线 | 0 | 0 / 0 | 无 |
| 2026-09-04 | TASK-0002 发布前门禁（commit 1d9d19b） | 0 | 0 / 0 | Release 环境缺少 `gh`；任务转 blocked |
| 2026-09-04 | 阻塞复核：发现用户已建 2026.09.2 Release，2026.09.3 仍缺 | 0 | 0 / 0 | 阻塞缩小未解除；latest 解析 2026.09.2 |
| 2026-09-08 | TASK-0003 M0 preflight | 0 | 0 / 0 | `releases/latest` 仍解析 2026.09.2；`releases/tags/2026.09.3` HTTP 404 |
| 2026-09-08 | TASK-0003 M1 校准后 | 0 | 0 / 1 | TASK_STORAGE_PENDING（TASK-0003 未提交窗口），提交即消除 |
| 2026-09-08 | TASK-0003 M3 后全量验证 | 0 | 0 / 1 | 同上；87/87 tests、snapshot in sync、`git diff --check` OK |
| 2026-09-08 | TASK-0003 交接前门禁（M1-M3 提交后） | 0 | 0 / 0 | TASK_STORAGE_PENDING 已随提交消除；87/87、snapshot in sync、`git diff --check` OK |
| 2026-09-08 | GitHub Actions 首跑 run 34181086563（develop push，gate job） | 0 | 0 / 0 | runner 端执行与本地一致；unit tests、vault check、drift 检测全部 success |
| 2026-09-08 | TASK-0002 Release 发布后复核与 blocked→active | 0 | 0 / 0 | latest 已解析 2026.09.3；远端 tag 正确；Release 标题和正文为空，保持 active 待补齐元数据 |
| 2026-09-08 | TASK-0002 accepted 门禁（owner 元数据决定后） | 0 | 0 / 0 | 技术验收项全部 [x]；标题/notes 移入 Optional（D-0003） |
| 2026-09-09 | Vault 2026.09.4 升级终验 | 0 | 0 / 0 | 唯一 `vault/index.md` 提案经 owner 确认后合并；106/106 tests、中英 snapshot in sync、`git diff --check` OK |
| 2026-09-09 | TASK-0008 M5 终验（vault 更新提交前） | 0 | 0 / 0 | 代码里程碑期间 check 输出与 M0 审计基准（`55ae985`）逐字节一致；本行留档后 runtime.md 随本任务编辑更新，测量变为 bytes 11469 / 27 entries，发现保持 0 / 0；116/116 tests、snapshot in sync、`git diff --check` OK |
| 2026-09-09 | TASK-0008 owner review round 3×P1 闭合（vault 更新提交前） | 0 | 0 / 0 | 原因码改按 finding phase 推导（owner 复现输出实际码 CLOSED_LOCAL）；补 3 项测试；golden B/C 仍逐字节一致；snapshot in sync、`git diff --check` OK |
| 2026-09-11 | TASK-0009 M0 方案与交接（提交前） | 0 | 0 / 1 | 唯一 warning 为新 tracked TASK 的预期 `TASK_STORAGE_PENDING`；五个历史 commit 存在、snapshot in sync、`git diff --check` OK。GLM 提交 M0 后必须重跑并消除此 warning |
| 2026-09-12 | TASK-0009 M5 终验（vault 同步提交前） | 0 | 0 / 0 | check 0/0、双 snapshot in sync、`git diff --check` OK；五个冻结 commit 在场；M1（`4773950`）后 protected 路径（scripts/init/skills/README/VERSION/MIGRATIONS/AGENTS）零改动；独立 review Round 2 APPROVE |
| 2026-09-13 | TASK-0009 验收 + 方案 B 执行前终验 | 0 | 0 / 0 | check 0/0、双 snapshot in sync、范围级 whitespace CLEAN；独立 review Round 4 APPROVE；owner 验收 accepted（结论锁定，D-0008）；原始 bundle + SHA-256 归档已在仓库外就位；历史重写按 owner 批准顺序执行 |
| 2026-09-16 | TASK-0012 M5 终验（实现提交 `bbae794` 后、Vault 收尾前） | 0 | 0 / 0 | 136/136 tests、status 0 unresolved、双 snapshot in sync、`git diff --check` clean；structured review 初轮 2×P1 已 fail-closed 修复，复审无 open P0/P1/P2 |
| 2026-09-16 | TASK-0012 accepted push / 2026.09.7 发布门禁 | 0 | 0 / 0 | develop `cf7e06a` 对应 GitHub Actions run 35076645891 success；tag 与 Release 已发布；Release 非 draft/非 prerelease、正文为空，latest 解析 2026.09.7 |
| 2026-09-18 | TASK-0004 M2：Orion 首次真实 local 项目检查 | 2 | 1 / 0 | `TASK_RUNTIME_CLOSED_LOCAL`：accepted local TASK-0001 仍在 runtime 与 Focus；修复待在 Orion 仓库执行，完成后需复跑至 0/0 |
| 2026-09-20 | TASK-0013/0014 第二轮安全终验（提交前） | 2 | 2 / 1 | 177/177、双语 snapshots 与 whitespace 通过；2 errors 仅为 owner 排除的 code-comments/stamp 现场，1 warning 为未提交 tracked TASK-0014；status 无 unresolved |
