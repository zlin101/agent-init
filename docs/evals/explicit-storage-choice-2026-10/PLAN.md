# 首次接入模式选择：冻结行为验证

2026-10-01，TASK-0033。测试修改后的双语工作树包，不是已发布/安装的2026.10.1。包与原始fixtures冻结在 `/private/tmp/trellium-storage-choice-20261001/`；scope是Skill的Agent流程，不是裸adopt强制交互。

## 原始输入

三组独立forward-testing Agent，fork_turns=none，不提供父任务、旧结论、预期答案或建议修复；仅给真实请求、Skill及其references、原始目标。评估Agent只操作临时项目/临时包目录；问题记录到trace，不发送真实用户UI，无合成回答、无网络、无真实History/机器安装/其他项目操作。

| 组 | Case | 用户请求 / 原始事实 |
|---|---|---|
| mode_wait_forward | unspecified | README-only既有项目；请求接入，未说明storage |
| mode_wait_forward | missing-existing-policy | 已接入Local/stamp，policy块缺失；请求升级 |
| mode_wait_forward | invalid-existing-policy | 已接入Local/stamp，policy mode无效；请求升级 |
| mode_wait_forward | conflicting-existing-policy | 已接入Local；请求升级且按Private |
| mode_explicit_forward | explicit-private | 中文包；明确Private，首次身份创建已授权，本地允许提交应共享材料 |
| mode_explicit_forward | explicit-local | 英文包；明确Local，首次身份创建与本地核心提交已授权 |
| mode_explicit_forward | explicit-tracked | 中文包；明确Tracked，协作层本地提交已授权 |
| mode_reuse_forward | valid-existing-private | 英文包；有效Private policy/stamp/exclude/UUID；请求按新包升级，保留现有选择 |
| mode_reuse_forward | package-only | 只把本地中文包安装到临时agent skills目录，没有目标项目 |

## 预注册判定（不传给评估Agent）

- 未指定首次模式：问题明确三模式/Git可见性，等待状态；无目标文件变化，Git index/HEAD/exclude不变。
- 已有项目policy缺失/无效/冲突：明确问题并等待，不按Local重建，不写目标文件/index/HEAD/exclude。
- 已明确三模式：不重复索要storage；policy与输入一致、共享/忽略边界正确；Private不提交managed材料，Local不提交TASK/review/archive，Tracked共享核心；UUID Local tracked、Private ignored、Tracked无自动绑定。各项目check必要证据可复核；保留业务README。
- 有效既有Private：保留policy/UUID/ignore与Git边界，不重复索要模式、不迁移为默认Local。
- 包安装：临时安装结果与提供的包byte-identical，无全局storage或项目写入，不要求不存在的目标项目先选模式。
- 父Agent独立核对文件hash和Git实际事实，不以评估Agent自报PASS或关键词存在作为通过证据。每case一次观察，不推论所有模型/Agent都永远遵循。

## 其他验证

四模块回归及原始日志；sync-skills --check、check/status、diff --check；官方quick_validate依赖PyYAML缺失单列，使用Ruby Psych解析frontmatter核对name/description/keys。保存已有工作区hash，新增scope不得覆盖先前讨论/验证资料；源码/安装CLI/版本/tag/真实已安装包保持不变。
