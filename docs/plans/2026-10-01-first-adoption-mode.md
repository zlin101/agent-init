# 首次项目接入模式选择：执行计划

2026-10-01；TASK-0033。Owner 要求先交付执行计划；扩展验证已停止。本计划收敛后续工作范围，不把现有工作树改动当作已验收或已发布。

## 目标

第一次给某个项目接入 Trellium 时，如果用户尚未明确选择 Private/Local/Tracked，先说明 Git 可见性并询问，回答前不写目标项目。已有明确选择直接复用；已有有效 policy 的项目保留模式。Local 仍是推荐项，不能代替用户回答。

机器级 Skill 安装与项目接入分开：只安装包、没有目标项目时，可以完成包安装，模式问题在首次项目接入时提出。

## 范围

- canonical 接入规则：70-adoption-flow 作为选择门定义，60-initialization-flow 与10-vault只同步必要摘要。
- 双语 SKILL 与protocol-model引用同一规则；sync-skills更新嵌入快照。
- D-0017替代D-0012的未指定fallback，记录授权、任务与执行证据；MIGRATIONS保留Unreleased条目。
- 不改源码、安装脚本、CLI、schema、模板policy默认值、现有项目模式、版本号或已发布tag。
- 个人习惯问答、Go Profile漏路由修复、发布和本机重装分别处理。

## 执行步骤

1. **整理已完成改动。** 核对双语入口与canonical语义一致，删除当前有效的未指定Local写入fallback，保留旧Decision/MIGRATIONS历史。首次接入选择门必须位于adopt及目标TASK契约写入之前。
2. **用已有证据完成最小验证。** 核对三类行为：未选模式提问且目标零写入；已明确模式不重复问；已有有效policy升级保留模式。已完成的异常policy与纯包安装案例作为补充，暂停的完整三模式接入不再整组重跑；若发现具体缺证据，只补该缺口，不重复执行完整项目治理/提交/升级流程。
3. **收尾一致性与审查。** 跑sync --check和diff --check，确认新任务之外没有新增仓库error；已有284项回归结果保留，不因仅收尾记忆更新重复全量测试。核对任务scope及先前未提交资料未被覆盖，提交简短结果与限制。

## 验收标准

- 未回答不运行adopt、不创建目标TASK契约、不写目标文件；允许只读扫描。
- 明确选择沿用，不重复问；有效旧policy保留；缺失/无效/冲突先澄清。
- 不把默认推荐、预选或超时当作用户答案，无全局storage配置。
- 双语与快照同步；真实行为证据与结构检查分开描述，不以关键词或Agent自报PASS冒充目标事实。
- 不更改已发布版本、本机Skill或真实项目，不代替Owner acceptance。

## 当前状态

- 已完成：工作流与canonical文字修改、双语快照、决策/任务记录；四个需澄清案例零目标写入；有效Private升级复用原模式；纯包安装不询问项目模式。
- 部分完成：三个明确模式案例已执行到不同接入阶段；其Agent在Owner提出“先出计划”后被中断，原trace与fixture保留，不记整组通过。
- 已有检查：284 tests /283 PASS /同一预存ancestor-swap FAIL；sync与diff检查通过；仓库check为0 errors/1新TASK未提交warning。官方quick_validate缺PyYAML，替代YAML frontmatter解析通过，此限制保留。
- 未完成：收敛行为证据的父Agent核对、最终范围审查、Owner acceptance。未commit/push，未tag或重装。

## 为什么耗时过长

原本是限定的Skill流程改动，执行却扩展成9个场景，并让评估Agent完整接入临时项目、创建契约、定制记忆、提交Git和处理升级proposal；主要等待集中在完整三模式接入组。验证负担超过这次改动需要，执行前的计划没有以独立可审阅载体先交付。本计划保留已经取得的证据并缩小剩余验证。
