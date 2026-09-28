# D-0003 - GitHub Release 元数据降为可选改进（2026-09-08）

Status: Superseded by D-0013

## Background

2026.09.3 Release 已发布且 `releases/latest` 解析正确，但 API 返回 `name=""`、`body=""`；TASK-0002 原契约把标题与 notes 列为验收 Gate，形成唯一残余缺口。

## Decision

Owner 于「09.3 Post-release Validation」方案 M0 决定：Release 验收 Gate 为——指向既有正确 tag、非 draft、非 prerelease、`releases/latest` 解析到该版本；标题与 notes 降为可选改进，不再阻塞任务关闭。

## Rationale

`install.sh --fetch` 等所有机器路径只依赖 tag 与 latest 解析；标题/notes 仅影响人类阅读体验。为可选的人类体验阻塞治理闭环，摩擦大于收益。

## Alternatives

- 阻塞等待 owner 在 UI 补齐元数据：被否，收益不抵摩擦；事实仍记录在 TASK-0002 的 Optional 条目中，随时可补。

## Impact

后续 Release 类任务的验收不再把元数据当 Gate；引用本决策时注意其适用边界——发布对象本身缺失或 tag 错误仍是不折不扣的失败。
