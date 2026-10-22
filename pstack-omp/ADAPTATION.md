# pstack → omp 适配记录

把 Cursor 插件 pstack（55 skills + 2 agents + 24 playbooks）改造成 omp 可用的 Agent Plugins 标准插件包。本文记录映射决策与可复用经验，供未来适配其他 agent 平台参考。

- 上游：`https://github.com/cursor/plugins`，pstack v0.15.29（commit 88d4751）
- 产物：`pstack-omp/`（本目录），Agent Plugins 1.0.0 标准包
- 权威映射表：`docs/harness/omp.md`（会话级读一次，所有 skill 共同遵守）

## 适配总策略

沿用上游自己的移植模式：pstack 官方就带一份 `docs/harness/claude-code.md`，把 Cursor 机制名映射到 Claude Code，skill 正文保持 Cursor 写法。我们照做：写 `docs/harness/omp.md`，skill 正文里 Cursor 机制名按映射落地改写（而非保留 Cursor 原词让模型现查映射——omp 的 skill 每次调用注入全文，正文直接是 omp 写法更可靠，省一次间接层）。

与上游 claude-code 方案的唯一分叉：Cursor 正文保留、靠表翻译 vs omp 正文直接改写。理由：

1. omp skill 注入是全文注入，正文写对了一劳永逸，不依赖模型先读映射表再自我翻译（上游方案要求"read this file once per session"，模型经常跳过）。
2. pstack 的机制引用是行为语义（spawn 字段、模型路由、transcript 路径），错一个字段 task 调用直接被 schema 拒绝，静默漂移比显式改写更危险。
3. 代价：上游更新时需要重新对 diff。用 git 仓库承载 pstack-omp，上游 commit 88d4751 为基线，后续可 `git diff` 驱动增量适配。

## 平台差异清单（Cursor → omp）

### 插件打包

| 维度 | Cursor | omp |
| --- | --- | --- |
| 包格式 | `.cursor-plugin/plugin.json` + root `plugin.json` | Agent Plugins 1.0.0 root `plugin.json`（`$schema: agent-plugins.org/schemas/1.0.0`） |
| skills 布局 | `skills/<name>/SKILL.md` | 相同（provider 一层扫描，非递归） |
| agents 布局 | `agents/*.md`（Cursor agent 格式） | `agents/*.md`（omp task-agent frontmatter：name/description 必填，tools CSV，model 可用 `@role` 别名） |
| 安装 | `/add-plugin pstack` | `omp plugin link <path>`（本地开发）；或 marketplace |
| 发现优先级 | — | agent-plugins provider priority 75 |

### 子代理（最深的差异）

| Cursor Task 字段 | omp task 对应物 |
| --- | --- |
| `subagent_type` | `agent`（agent 名，指向 agents/*.md 定义或 bundled） |
| `model`（per-item） | **不存在**。模型路由下沉到 agent frontmatter `model: "@role"` + `modelRoles` 设置 |
| `readonly: true` | 只读 agent（tools 限制在 frontmatter）或 bundled `scout` |
| `environment: "cloud"` | Jules cloud session（`poteto-mode/scripts/jules-cloud.mjs`，REST API，`AUTO_CREATE_PR`）；需机器本地保留时才用 `isolated: true` |
| `run_in_background` | 不需要：`async.enabled` 默认开，一切后台化 |
| `resume` | `write agent://<id>`（活/驻留 agent 消息即复活） |
| （无） | `solutionSpace` **必填**：子问题开放度描述，喂给思考分级器 |

**核心教训：Cursor 的 model-per-task-item 在 omp 是 model-per-agent-type + modelRoles。** 适配多模型面板（arena/interrogate 的"每席位一个模型"）需要为每个席位造一个命名 agent（`pstack-panel` = `@pstack-panel`），skill 正文说 agent 名，setup skill 写 modelRoles 值。用户换模型只动 config.yml，不动 skills。

### 模型配置

- Cursor：`~/.cursor/rules/pstack-models.mdc`（always-apply 规则，role→slug 行）。
- omp：`modelRoles` in `~/.omp/agent/config.yml`。`@pstack-fast`/`@pstack-judge`/`@pstack-panel` 三个角色；值形如 `provider/model:thinking-level`（`:max`/`:xhigh`/`:high`/`:medium`/`:low`）；未设置即继承父会话模型（= Cursor 的 `inherit-parent`）。
- 模型检测：`omp models`（列模型+支持档位）。Cursor 的 slug 探测逻辑换成这条 CLI。

### 会话/transcripts

- Cursor：`~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`。
- omp：`~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl`；`<encoded-cwd>` 规则：home 相对 `-<rel>`、temp 相对 `-tmp-<rel>`、其他 `--<abs>--`，分隔符全转 `-`。子代理 transcript 经 `history://<id>` 读（渲染为简洁记录，优于手工解析 JSONL）。
- 影响 skills：recall（聊天考古）、reflect（transcript 评审）、automate-me（习惯挖掘）、session-pickup playbook。

### Cursor-only 能力 → 跳过策略

omp 无对应物的（Automations/Bugbot）：skill 步骤保留，执行时输出一行 `Skipped in omp: <step>. <reason>.` 继续走，不询问不重试。有 omp 替代物的不是 skip：`cloud agents`→Jules REST API（`jules-cloud.mjs`）、`/loop`→omp 内置 `/loop`、`deslop`→unslop skill、`control-ui`→browser 工具、`control-cli`→bash 实跑、内置 PR 工具→`gh`/`pr://`、`create-skill`→authoring-a-skill playbook。

### frontmatter 兼容性

- `disable-model-invocation: true`：omp 归一化为 `hide`，skill 仍装载、仍可 `skill://<name>` 与 `/skill:<name>` 到达——pstack 全部 skill 都带它（设计意图：只由 poteto-mode 显式路由，不靠模型自觉触发），语义完整保留。
- `name`/`description`：两个平台同构，触发词不受影响。
- `icon`/`color`：omp 不识别，删除（保留亦无害，但清理干净）。
- `paths:`（typescript-best-practices）→ omp 的 `globs:`。
- `argument-hint`：omp 未知字段，保留无害。

### 引用与路径

- skill 间相对引用 `../<name>/SKILL.md`、`references/…`、`playbooks/…`：omp 注入 invocation 时附带 skill 目录（`[Skill directory: <baseDir>]`）并指示相对路径以它为基准；`skill://<name>/<path>` 也可解析。相对形式全保留。
- 原版 "put this file's absolute path in every subagent prompt" → "put the skill directory announced in the invocation message in every brief"。

## 适配方法（可复用流程）

1. **先读目标平台文档再定方案**。本次关键事实全部来自 `omp://skills.md`、`omp://tools/task.md`、`omp://task-agent-discovery.md`、`omp://settings.md`、`omp://session.md`：skill 装载布局、task schema 字段、agent frontmatter 契约、session 路径编码、模型枚举 CLI。装作已知平台行为会埋雷。
2. **量化依赖密度再分工**。`grep -ciE "…cursor tokens…" 每 file` 排序：24 命中（setup-pstack）到 0 命中（22 个 principle skills）。principle 类零依赖直接保留；高依赖的 setup/poteto-mode/reflect 单独深改。
3. **共享契约文件 + 扇出**。把映射决策写进 `local://pstack-omp-contract.md` 和 `docs/harness/omp.md`，4 个子代理（路由类/poteto-mode/内容类/agents）并行改写，各自 grep 自查禁词清零。
4. **禁词表作为验收**：`cursor|subagent_type|AskQuestion|grok-4|claude-opus|run_in_background|readonly:|environment: "cloud"|\.cursor|agent-transcripts|/loop|bugbot|create-skill` 在产物中应为 0 命中。
5. **实测安装与冒烟**（见下）。

## 验证

- **安装/冒烟**：`omp plugin link` 后 59 个 skill、16 个 playbook、5 个 agent 可发现；禁词扫描清空（云/Bugbot 段落除外）。
- **worktree 审计**：临时 git 仓库 + worktree + 伪造 session JSONL，`LAST_CHAT` 输出了正确日期，bucket 从 `safe` 变为 `verify-recent-chat`；当前仓库解析到 `~/.omp/agent/sessions/--D--codex_project-pstack-ports--`。
- **Jules CLI 试跑**：session 可创建、可并行、可 `remote pull` 出 patch；但 `--session` 会在 `#` 截断，只读任务取不到文字结论，PR 不自动创建。
- **Jules API 试跑**：`AUTO_CREATE_PR` 在约 4 分 09 秒内产出 PR，`outputs[].pullRequest` 直接给 URL，`activities` 可读计划、进度和 agent 消息；关闭 PR/删分支后 session 可能回到 `IN_PROGRESS`，`wait` 以超时退出。
- **适配器冒烟**：`sources`、`dispatch --no-pr`、`status`、`wait`（超时路径）、`send`、`result`、`activities` 均对真实 Jules API 跑通；只读 session 的 `result` 返回 `SEND_OK`。

## 已知限制

- 模型多样性依赖用户配置：三个 `@pstack-*` 角色未配置时全继承父模型，arena/interrogate 的"跨家族面板"退化为同模型多席位。setup-pstack 引导配置时解决。
- `isolated: true` 要求 `task.isolation.enabled: true`（omp 默认 off），skills 降级为共享 checkout + 注明。
- Jules 云 worker 依赖 `JULES_API_KEY` 和已授权的 GitHub 仓库；API 无 cancel 端点，只读 session 答完后可能长期停在 `IN_PROGRESS`，要用 `result` 读答案而不是等 `COMPLETED`。
- Qoder Cloud Agents MCP 未作为默认路径：它是通用沙箱，需 setup script 自行 clone，且不自动产出 PR。
- omp 无 per-item effort 默认暴露（`task.enableEffort` 默认 off）：思考档位随 modelRoles 的 thinking 后缀走。
- benny automations（上游 automations/ 目录，Issue 自动化）未纳入本包：其价值依赖 Cursor Automations 运行时，omp 无 webhook/常驻例程机制。留在上游，未来 omp 出现等价物再评估。
