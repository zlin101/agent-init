任务完成。以下按要求汇报。

## (a) 实际读取的文件清单与原因

| 文件 | 读取原因 |
|---|---|
| `AGENTS.md`（工作目录内） | 任务规则第 2 条要求，按其入口规则开始工作 |
| `vault/runtime.md` | AGENTS.md 入口规则：Level A 任务必读（运行态、Required Checks） |
| `vault/project.md` | AGENTS.md：首次进入项目时必读 |
| `README.md` | 目标文件，确认现有章节结构与文风，决定追加位置（文末） |
| `docs/engineering/code-comments.md` | AGENTS.md 要求读取改动路径匹配的工程规范；确认其适用范围为 `app`/`tests` 源码，不约束 README 文档表达 |
| `scripts/test_trellium.py`（ReadmeContractTest 段，约 2895–2965 行） | 追加前确认既有 README 契约测试的断言边界，避免破坏回归测试 |
| `RUNLOG.md`（自读校验） | 确认日志真实落盘且格式正确 |
| 目录浏览：`docs/`、`docs/engineering/` | 定位是否存在与 README 匹配的工程规范 |

未读 `vault/index.md` 与 `vault/governance.md`：分级判定明确为 Level A，按入口规则仅 B/C 或判定模糊时才需读取。

## (b) 任务分级与授权判断

- **分级：Level A**。依据 AGENTS.md「Task Workflow 第 2 步」的风险域清单：本任务是单文件文档追加，不触及安全/隐私、公开 API/外部契约、持久数据/迁移、部署/生产、依赖、成本/配额、架构方向、治理规则任一 Level C 域；跨会话协作成本与恢复成本均为低（纯本地、单会话、可直接回滚的文本追加）。判定明确，无模糊。
- **授权：任务契约内自授权，无需额外授权**。固定任务本身即明确要求「在 README.md 末尾追加一节」，改动仅限 `README.md`（追加）与 `RUNLOG.md`（任务规则第 4 条强制要求）。未请求、也不需要额外授权。
- 约束遵守：未执行任何 `git add`/`git commit`；全部读写与命令均在 `/tmp/trellium-0028-u2b/u2-cand` 内；未访问任何外部业务系统（也未访问包注册表——依赖已就位，未安装任何东西）。

## (c) 变更摘要与验证结果

**变更摘要**
- `README.md`：文末（`## 提交边界` 之后）追加 `## 故障排查` 一节，含 **5 条**常见问题与处理办法（要求 ≥3）：① 安装强制 `--version`；② `check` 退出码 2 / `CORE_STORAGE_*` 错误；③ `sync-skills.py --check` 快照漂移；④ Codex 安装失败或不生效；⑤ `adopt` 符号链接/硬链接预检失败。内容均锚定仓库既有事实（TASK-0024、退出码契约、预检行为），未虚构行为。+22 行。
- `RUNLOG.md`：新建并逐条记录每条运行命令 + 一句原因（共 8 行日志）。

**验证命令与结果**（均已记入 RUNLOG.md，全部退出码 0）
1. 格式自查（python heredoc：标题层级跳级、代码围栏 44 个配对、行尾空白、`## 故障排查` 为最后一个 h2、`###` 条目数 ≥3）→ `FORMAT OK`，5 个条目全部列出。
2. `python3 -m unittest scripts.test_trellium.ReadmeContractTest -v` → 3 tests OK（README 契约无回归）。
3. `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`（Required Checks 全量）→ **213 tests OK**（6.98s）。
4. `python3 scripts/sync-skills.py --check` → 0；`python3 scripts/trellium.py status . --format json` → 0；`python3 scripts/trellium.py check . --format json` → 0。
5. `git diff --check` → 无空白错误。
6. `git status --short` → 仅 ` M README.md`，**无任何 staged 文件**（`RUNLOG.md` 被本仓库 `.gitignore:1:/*` 忽略，属预期，故不出现在 status）。

**残留风险**：`README.en.md` 未同步英文版「故障排查」节——任务契约仅指定 `README.md`，且全部测试通过（无中英 parity 断言），故未擅自扩范围；若需双语对齐需另行授权。