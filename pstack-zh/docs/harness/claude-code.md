# 在 Claude Code 中使用 pstack

`pstack` 的 `skill` 正文使用的是 Cursor 名称。在 Claude Code 里，每次会话先读一遍本文件，然后按下面几张对照表把 `skill` 里的 Cursor 名称映射成 Claude Code 对应写法。文中 `<pstack>` 指存放 `skills/` 和 `docs/` 的插件目录。如果某个 Cursor 字段表里没有对应项，直接省略并说明即可，绝不要向工具传 schema 不接受的字段或取值。

## 工具映射

| Cursor | Claude Code |
| --- | --- |
| `Task` | `Agent` |
| `AskQuestion` | `AskUserQuestion`。在 `-p` 非交互模式下不可用，改为直接用纯文本提问。 |
| 打开待办清单（todolist），或把步骤抄进 todolist 工具 | 会话提供 `TodoWrite` 时就用它；否则在回复里维护清单并在每个阶段更新。 |
| 调用另一个 `pstack` skill（`/name` 或「**name** skill」） | 直接用 `Read` 读取 `<pstack>/skills/<name>/SKILL.md` 并照着执行。`Skill` 工具会拒绝大多数 `pstack` skill。提醒用户手动敲命令时，写成 `/pstack:<name>`。 |
| `Grep`、`Glob` | 会话里没有 `Grep` 或 `Glob` 时，用 `Bash` 跑 `rg`。 |

## 子代理字段

| Cursor | Claude Code |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `poteto-agent`、`comment-sicko` | `pstack:poteto-agent`、`pstack:comment-sicko` |
| `poteto-agent` 文件里的 `model:` 行 | 里面写的是 Cursor 模型 `slug`。每次调 `Agent` 派生 `pstack:poteto-agent` 时，都按「模型映射」表显式传 `model` 和 `effort`，防止那个 Cursor `slug` 传到 API。 |
| `readonly: true` | `subagent_type: "Explore"`。注意它仍保留 `Bash`，所以 `brief` 里也要写明「不要编辑文件」，事后检查 `git status`。 |
| `readonly: false` | `general-purpose`，会保留主会话的 MCP 服务器。 |
| `environment: "cloud"` | `isolation: "worktree"`，并在 `brief` 里写明工人要切出的分支或 commit。 |
| `environment: "local"` | 省略。 |
| `cloud_base_branch: <b>` | 在 `brief` 里指示工人先切出 `<b>`。 |
| `run_in_background: true` | 省略。子代理默认在后台运行，完成后会自动通知。 |
| `resume` | 新起一个代理，把前一次的结果贴进它的 `brief`。 |
| `file_attachments` | 在 `brief` 里列出文件路径。 |

## 模型映射

| Cursor | Claude Code |
| --- | --- |
| `claude-<family>-<version>-<effort>[-fast]`（如 `claude-opus-5-5-xhigh`） | `model: "opus"` 与 `effort: "xhigh"`。`model` 只接受 `opus`、`sonnet`、`haiku`、`fable`，去掉 `-fast`。 |
| `gemini-*` 或其他非 Claude 模型 `slug` | 省略 `model` 让代理跑在主会话模型上，并如实说明。 |
| `auto` 或 `inherit-parent` | 省略 `model`。 |
| `pstack-models.mdc` 规则（`~/.cursor/rules/pstack-models.mdc`） | `~/.claude/rules/pstack-models.md`。Claude Code 会在每次新会话自动加载它，所以各角色配置行已经在上下文里；如果不在就读该文件。文件或对应角色行缺失时，沿用 `skill` 默认 `slug`。 |
| 角色值 `<model> <effort>`（如 `opus high`） | `model: "opus"` 与 `effort: "high"`。 |

## `setup-pstack` 差异

Claude Code 会在每次新会话加载 `~/.claude/rules/` 下的所有 `.md` 文件，因此 `setup-pstack` 把规则写在这里。照着它的步骤跑，只需调整这三点：

- **探测模型。** 可用模型取自 `Agent` 工具 schema 列出的 `model` 值，每个搭配其 `effort` 可选档位。真实模型写成 `<model> <effort>`，例如 `opus xhigh`。`effort` 放在最后一个词，这样预算升降档步骤可以原样照跑。
- **默认值映射。** 按上面表格映射每个默认 `slug`：`claude-opus-5-5-xhigh-fast` 对应 `opus xhigh`，`claude-opus-5-5-high-fast` 对应 `opus high`，`claude-fable-5-2-high` 对应 `fable high`，`gemini-4-neon-xhigh` 对应 `inherit-parent`。
- **写入文件。** 写入 `~/.claude/rules/pstack-models.md`，不要写 frontmatter，直接放注释行、`# budget` 行以及第 5 步的各角色配置行。整文件覆写。绝不要把角色行写进 `CLAUDE.md` 或 `AGENTS.md`。

## 路径映射

| Cursor | Claude Code |
| --- | --- |
| `.cursor/skills/`、`~/.cursor/skills/` | `.claude/skills/`、`~/.claude/skills/` |
| `~/.cursor/plugins/`、`.cursor-plugin/plugin.json` | `~/.claude/plugins/`、`.claude-plugin/plugin.json` |
| `.cursor/rules/*.mdc`、常驻规则 | `CLAUDE.md`，没有时用 `AGENTS.md`。Claude Code 不读 `.mdc` 文件，模型规则文件除外（见上文「模型映射」）。 |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | 文件存在时读本地 `<pstack>/<path>`。插件随包附带 `skills/`、`docs/guide/` 和 `README.md`，直接读本地副本，别去联网抓。只有用户需要外链时才给 URL。 |
| `~/.cursor/projects/<slug>/agent-transcripts/` 下的对话记录 | `~/.claude/projects/<slug>/<session>.jsonl`。这里的 `<slug>` 是工作区路径把每个 `/` 和 `.` 换成 `-`（例如 `/Users/you/proj` 变成 `-Users-you-proj`）。该目录下最新的 `.jsonl` 就是当前会话，其 `<session>/subagents/` 子目录存放子代理记录。只读当前工作区对应的目录。 |

## Cursor 专属功能处理

Claude Code 没有 Cursor Automations、Bugbot、Cursor 云端代理，也没有内置 PR 工具。步骤遇到无对应物的功能时，在回复里写一行 `Skipped in Claude Code: <step>. <reason>.`，然后直接走下一步，不要停下、不要询问、也不要重试。如果后面步骤依赖跳过步骤的产物（比如 URL 或密钥），留一个占位符并在这行跳过说明里点出来。

| Cursor | Claude Code |
| --- | --- |
| Cursor Automations：routines、`update_state` routine 调用、`api2.cursor.sh/automations` webhook、routine 唤醒与 `SendToUser` 密钥请求 | 输出跳过行后继续。 |
| Bugbot | GitHub PR 上的 Bugbot 评论属于普通评审线程，直接用步骤里的代码托管平台命令正常分诊。如果 PR 上没有 Bugbot 检查或评论，涉及启动、等待或配置 Bugbot 的步骤输出跳过行。 |
| Cursor 云端代理 | `environment: "cloud"` 映射为 `worktree`（见「子代理字段」）。涉及云端代理本身（例如它的后台面板状态或独立虚拟机）的步骤输出跳过行。 |
| 内置 PR 工具 | 使用步骤里给的代码托管平台命令，例如 `gh pr create`。这不算跳过，不要输出跳过行。 |
