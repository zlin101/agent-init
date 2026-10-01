# 首次接入模式选择：父 Agent 独立核对结果

2026-10-01，TASK-0033。执行[冻结验证计划](PLAN.md)的收敛核对步骤：以冻结现场 `/private/tmp/trellium-storage-choice-20261001/` 的实际文件 hash 与 Git 事实独立复核，不采信评估 Agent 自报。核对工具为本目录 `audit_targets.py`（判定标准来自 PLAN.md 预注册项）。

## 核对结论

`python3 audit_targets.py` 于 2026-10-01 重跑：**38/38 项全 PASS，exit 0**。

| 组 | 用例 | 独立核验事实 |
|---|---|---|
| mode_wait | unspecified / missing / invalid / conflicting-existing-policy | 四个目标 snapshot 逐字节未变（文件 hash + Git index + HEAD + exclude 均与 before 快照一致）；目标零写入 ✓ |
| mode_explicit | explicit-private | policy = private；managed material 不在 index；project-id 被 exclude 覆盖；index/HEAD 保持；checker 0 error；业务 README 未动 |
| mode_explicit | explicit-local | policy = local；协作核心全部 tracked；TASK/review/archive 命中窄 .gitignore 且不入 index；project-id tracked；checker 0 error |
| mode_explicit | explicit-tracked | policy = tracked；协作核心 tracked；TASK 命名空间不被 ignore；无自动身份绑定；checker 0 error |
| mode_reuse | valid-existing-private | policy/UUID/exclude/project 数据全部保留未变；不重复索要模式；不迁移为默认 Local |
| mode_reuse | package-only | 安装结果与源包逐字节一致；无全局 storage、无项目写入 |

三个 explicit 用例的 trace（`mode_explicit_forward.json`）记录 `questions: []` 且决策含 "Reuse the explicit storage mode scoped to this user request; no mode question"——与"已有明确选择不重复询问"一致。四个需澄清用例 trace（`mode_wait_forward.json`）记录停在提问等待状态、harness 声明无真实用户 UI 消息/无合成回答/无网络/无 History 写入。

## 三组 explicit 用例的中断边界

Owner acceptance（2026-10-01）：Owner 在 Codex review 通过后明确“你验收通过，我就通过”，交付已接受。未授权或执行 commit/push/tag/重装；下文保留原验证过程与限制。

评估 Agent 在 owner 要求"先出计划"后被中断，属于接入后段的治理/定制/提交阶段；**选择门相关的核心行为（不重复询问、policy 写入、Git 边界、身份绑定、checker 通过）已完整发生并被冻结现场证实**。按计划不重复执行完整项目治理/提交/升级流程。

## 证据限制（如实披露）

独立评审复核（2026-10-01，Codex）：审计重跑 38/38 PASS；两侧冻结测试包与当前工作树逐文件 SHA-256 一致；提问与复用轨迹符合选择门。canonical、双语与 scope 审查未发现阻塞问题；sync、check（0 errors/1 TASK 未提交 warning）、status（0 unresolved）及 diff --check 通过。TASK review gate 通过，Owner acceptance 保留 pending。

- 每个 case 一次观察，不推论所有模型/Agent 永远遵循；关键词存在不作为行为证明，本核对以文件与 Git 事实为准。
- 官方 quick_validate 依赖 PyYAML 在本机缺失，frontmatter 校验使用替代 YAML 解析（Ruby Psych），该限制保留。
- 回归基线沿用冻结 `regression.txt`（284 tests / 283 PASS / 1 FAIL，唯一 FAIL 为预存 ancestor-swap 环境失败，干净基线可复现）；本轮收尾未改产品代码，不重复全量测试。
- 测试对象是修改后的双语工作树包，不是已发布的 2026.10.1 包；发布与真实目标接入不在本任务范围。
- 冻结现场位于 `/private/tmp`，属临时证据；本目录保存判定标准、审计脚本与本核对记录，原始 trace/fixture 以冻结目录为准。
