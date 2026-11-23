# omp 平台实测备忘（从 v1 归档提取）

本文件保留 v1 尝试阶段在 `omp`（oh my pi，实测版本 18.13.1）上踩过坑并已验证的平台事实，供后续基于 `pstack-zh` 重建中文版 `pstack-omp` 时直接复用。完整的 v1 原件封存在本地分支 `archive/v1-attempts`。

## 1. 插件打包与分发踩坑

- **禁止在包根放 `plugin.json`**：一旦存在根 `plugin.json`，omp 的 skill 发现会切给 `agent-plugins` 提供者的 Agent Skills 1.0.0 封闭字段校验。`disable-model-invocation`（以及 `hide`、`disableModelInvocation`）不在该封闭字段集内，会导致带该字段的 skill 被静默丢弃，而 `omp plugin doctor` 仍然报全绿。
- **正确清单形式**：只保留包内 `package.json` 的 `"omp"` 字段；跨目录分发走仓库根 `.omp-plugin/marketplace.json`（catalog 条目用 `"source": "./pstack-omp"`）。
- **消费者安装命令**：
  - `omp plugin marketplace add <owner>/<repo>`
  - `omp plugin install pstack-omp@pstack-ports`
  - 本地开发链接：`omp plugin link ./pstack-omp`
- **安装验收不能只看 `omp plugin doctor`**：必须新起会话用 `skill://` 逐个或全量核对实际加载数是否等于 `skills/` 目录数。

## 2. 工具与协议映射

| Cursor 原版 | omp 对应物 | 说明 |
| --- | --- | --- |
| `Task` | `task` | 批量派发用单次 `task` 调用里的 `tasks[]`，或并行 `task`；`solutionSpace` 为必填字段（一行描述开放度） |
| `AskQuestion` | `ask` | `-p` 非交互模式下 `ask` 不可用，改为纯文本提问 |
| TodoList | `todo` | `init` / `start` / `done` |
| 跨 skill 引用 | `skill://<name>/...` 或 `/skill:<name>` | 注入时 omp 会给出 `[Skill directory: <baseDir>]`，相对路径与 `skill://` 均可用 |
| `Grep` / `Glob` / `Read` / `Edit` / `Write` / `Bash` | `grep` / `glob` / `read` / `edit` / `write` / `bash` | `read` 原生支持 `skill://` 与 `history://` |
| Web 搜索 | `web_search` | — |
| `control-cli` / `control-ui` | `bash` / `browser` 工具 | CLI/TUI 用 `bash` 实跑；浏览器/Electron/Web UI 用 `browser` 工具 |
| `deslop` | `unslop` skill | omp 无 `cursor-team-kit` |
| `/create-skill` | `authoring-a-skill` playbook + `manage_skill` | — |
| `/loop` | omp 内置 `/loop [count\|duration] [--while\|--until <check>]` | 已通过 omp 二进制字符串交叉确认存在 |
| `/visualize` | 无独立命令 | `tui.autoGraph` 可对消息里的数值 Markdown 表格自动绘表 |
| 内置 PR 工具 | `gh` CLI 与 `pr://` | — |

## 3. 子代理、模型路由与只读保证

- **没有 per-item `model` 字段**：omp 的 `task` schema 为 `{ context, tasks: [{ name?, agent?, task, solutionSpace, effort?, ... }] }`，不支持 Cursor 的 `subagent_type`、`model`、`readonly`、`environment`、`run_in_background`、`resume`、`file_attachments`。
- **模型路由下沉到 agent frontmatter + `modelRoles`**：
  - 通过包内 `agents/*.md` 绑定 `@role` 别名，例如：`pstack-worker.md`（`@pstack-fast`）、`pstack-judge.md`（`@pstack-judge`）、`pstack-panel.md`（`@pstack-panel`），另加 `comment-sicko.md`。
  - `~/.omp/agent/config.yml` 中的 `modelRoles` 支持 `provider/model:thinking-level`（`:low` / `:medium` / `:high` / `:xhigh` / `:max`）；未设置时回退继承父会话模型（对应 `inherit-parent`）。
  - 可用模型与支持档位通过 `omp models` 枚举。
  - `task.enableEffort` 默认关闭，思考档位直接跟 `modelRoles` 后缀走。
- **只读机制区分**：
  - **工具级只读**：内置 `scout` 或专用白名单 agent（如 `pstack-reader`，frontmatter 设 `tools: read, grep, glob, web_search`）。
  - **指令级只读**：同一模型角色（如 `pstack-judge`）既要承担高难度代码改写又要充当评审席位时，不能禁用写工具，只能靠任务说明约束 + 事后检查 `git status` 复核。需要跑只读命令（如 `bash`）的席位同理。
- **后台与恢复**：`async.enabled` 默认开启，`task` 默认后台运行；延续已有子代理使用 `write agent://<id>`。

## 4. 关键全局设置与默认值陷阱

| 配置键 | omp 默认值 | pstack 所需值与原因 |
| --- | --- | --- |
| `task.isolation.enabled` | `false` | 必须为 `true`，否则 `isolated` 字段不存在，并行任务会静默退化成共享当前工作区 |
| `task.isolation.apply` | `true` | 建议设为 `false`。默认 `true` 会在隔离 worker 结束时自动把补丁打进当前 checkout，违背 pstack 先验证后合并的顺序；设为 `false` 后产物存为 `<Agent>.patch`，由父级显式应用 |
| `plan.defaultOnStartup` | `false` | 保持 `false`（或先退出 plan mode），否则 plan mode 会拒绝 `isolated` 字段和部分执行动作。注意：`plan.enabled` 只控制是否允许进入 plan mode，不决定启动默认态 |

## 5. 会话记录、云端 Worker 与 Windows 环境事项

- **Session / Transcript 路径**：
  - `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl`。
  - `<encoded-cwd>` 编码规则：home 下相对路径为 `-<rel>`，temp 下为 `-tmp-<rel>`，其余为 `--<abs>--`，路径分隔符统一转为 `-`（如 `D:/codex_project/pstack-ports` → `--D--codex_project-pstack-ports--`）。
  - 子代理记录可直接用 `history://<id>` 读取，无需手工解析 JSONL。
- **云端 Worker（待另寻方案）**：
  - 原 v1 尝试过的 Jules REST 方案已关停，对应脚本已从仓库移除。未来重建 `pstack-omp` 时，本地并行隔离用 `isolated: true`；若需要跨机器持久云端 worker，需届时另选替代方案。
- **Cursor 专属能力处理**：
  - `automations/`（benny）与 Bugbot 在 omp 无等价物。保留流程步骤时可采用单行跳过约定（如在回复注明原因后继续）；GitHub PR 上的其他人类或 bot 评审线程仍正常按规则分诊。
- **Windows 与 `statechart` / 测试环境**：
  - `.gitattributes` 必须对 `*.sh`、`*.bash`、`*.mjs`、`*.ts` 与 `pstack-*/skills/*/scripts/**` 强制 `text eol=lf`，否则 Windows checkout 成 CRLF 后，WSL 调脚本或 `statechart` 语料测试会失败。
  - 上游 0.15.36 起 `statechart` 已改为 TypeScript 编译器，在 Windows 下如需调用启动脚本可用 `sh skills/statechart/scripts/statechart ...` 或 `node skills/statechart/scripts/statechart.ts ...`（Node 24 实测可起）；TLC 依赖 `mise` 或环境变量 `TLA2TOOLS` / `JAVA`。
