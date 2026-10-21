# pstack 在 Claude Code 中

> 译自 cursor/plugins 0.15.29 `pstack/docs/harness/claude-code.md`（本地英文原文在 `../../../../upstreams/pstack/pstack/docs/harness/claude-code.md`）。

pstack 的 skills 用的是 Cursor 的名字。在 Claude Code 里，每个会话读一遍这个文件，然后用下面的表把 skill 里出现的每个 Cursor 名字映射过去。`<pstack>` 指存放 `skills/` 和 `docs/` 的那个目录。表里没有对应行的 Cursor 字段：直接丢弃，并说明丢掉了什么。绝不传工具 schema 不接受的字段或值。

## 工具

| Cursor | Claude Code |
| --- | --- |
| `Task` | `Agent` |
| `AskQuestion` | `AskUserQuestion`。`-p` 模式下没有这个工具，改用纯文本提问。 |
| 打开 todo 列表 | 会话提供 `TodoWrite` 就用它。否则把列表写在回复里，每个阶段更新一次。 |
| 运行另一个 pstack skill（`/name` 或「the **name** skill」） | `Read` `<pstack>/skills/<name>/SKILL.md` 然后照着做。`Skill` 工具对多数 pstack skill 会拒绝。要引导用户输入时，写 `/pstack:<name>`。 |
| `Grep`、`Glob` | 会话没有 `Grep` 或 `Glob` 时，用 `Bash` 跑 `rg`。 |

## 子代理字段

| Cursor | Claude Code |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `poteto-agent`、`comment-sicko` | `pstack:poteto-agent`、`pstack:comment-sicko` |
| `readonly: true` | `subagent_type: "Explore"`。它保留 `Bash`，所以任务简报里要写「不要改文件」，事后用 `git status` 核查。 |
| `readonly: false` | `general-purpose`。它保留会话的 MCP 服务器。 |
| `environment: "cloud"` | `isolation: "worktree"`。写明 worker 要检出哪个分支或 commit。 |
| `environment: "local"` | 省略。 |
| `cloud_base_branch: <b>` | 告诉 worker 先检出 `<b>`。 |
| `run_in_background: true` | 省略。子代理默认就在后台运行，完成后会通知你。 |
| `resume` | 另起一个新 agent，把之前的结果粘进它的任务简报。 |
| `file_attachments` | 把路径列表写进简报。 |

## 模型

| Cursor | Claude Code |
| --- | --- |
| `claude-<family>-<version>-<effort>[-fast]`，如 `claude-opus-5-5-xhigh` | `model: "opus"` 加 `effort: "xhigh"`。`model` 只接受 `opus`、`sonnet`、`haiku`、`fable`。去掉 `-fast`。 |
| `grok-*`、`gpt-*` 或其他非 Claude 的 slug | 省略 `model`，让 agent 跑在会话模型上，并说明这一点。 |
| `auto` 或 `inherit-parent` | 省略 `model`。 |
| `pstack-models.mdc` 规则，`~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md`。Claude Code 会把它加载进每个新会话，所以角色行已在上下文里。如果不在，读这个文件。文件或该角色的行缺失时，用 skill 的默认 slug。 |
| 角色值 `<model> <effort>`，如 `opus high` | `model: "opus"` 加 `effort: "high"`。 |

## setup-pstack

Claude Code 会把 `~/.claude/rules/` 里的每个 `.md` 文件加载进每个新会话，所以 `setup-pstack` 把规则写在那里。按它的步骤走，做以下调整：

- 检测。检测到的模型就是 `Agent` 工具 schema 列出的 `model` 值，各配一个它 `effort` 值里的推理力度。写成真实模型 `<model> <effort>`，如 `opus xhigh`。力度是最后一个词，所以预算那一步按原文照做即可。
- 默认值。用上面的行映射每个默认 slug：`claude-opus-5-5-xhigh` 是 `opus xhigh`，`grok-4.7-xhigh-fast` 是 `inherit-parent`。
- 写入。写 `~/.claude/rules/pstack-models.md`：不带 frontmatter，先是注释行，然后 `# budget` 行，再是第 5 步每个角色一行。整个文件覆盖写入。绝不要把角色行写进 `CLAUDE.md` 或 `AGENTS.md`。

## 路径

| Cursor | Claude Code |
| --- | --- |
| `.cursor/skills/`、`~/.cursor/skills/` | `.claude/skills/`、`~/.claude/skills/` |
| `~/.cursor/plugins/`、`.cursor-plugin/plugin.json` | `~/.claude/plugins/`、`.claude-plugin/plugin.json` |
| `.cursor/rules/*.mdc`、始终生效的规则 | `CLAUDE.md`，没有 `CLAUDE.md` 时用 `AGENTS.md`。Claude Code 从不读 `.mdc` 文件。模型规则是例外，见「模型」一节。 |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | 该文件存在时用 `<pstack>/<path>`。插件自带 skills、`docs/guide/` 和 `README.md`。读本地副本，绝不联网抓取。用户需要链接时再给 URL。 |
| `~/.cursor/projects/<slug>/agent-transcripts/` 里的对话记录 | `~/.claude/projects/<slug>/<session>.jsonl`。slug 是工作区路径里每个 `/` 和 `.` 都换成 `-`，所以 `/Users/you/proj` 就是 `-Users-you-proj`。该文件夹下最新的 `.jsonl` 就是当前会话。它的 `<session>/subagents/` 文件夹存子代理的记录。只读这个工作区的文件夹。 |

## Cursor 独有功能

Claude Code 没有 Cursor Automations、Bugbot、Cursor cloud agents，也没有内置 PR 工具。某一步需要它们时，在回复里写一行：`Skipped in Claude Code: <step>. <reason>.`（在 Claude Code 中跳过：<步骤>。<原因>。），然后继续下一步。不要停、不要问、不要重试。后面的步骤需要被跳过那步产出的东西（比如 URL 或密钥）时，留一个占位符，并在那一行里点名它。

| Cursor | Claude Code |
| --- | --- |
| Cursor Automations：routines、`update_state` routine 调用、`api2.cursor.sh/automations` webhook、routine 唤醒、`SendToUser` 密钥请求 | 按上面的方式跳过。 |
| Bugbot | Bugbot 在 GitHub PR 上的评论就是普通评审线程，用步骤里给的 forge 命令分诊。PR 没有 Bugbot 检查或评论时，跳过启动、等待或配置 Bugbot 的步骤。 |
| Cursor cloud agents | `environment: "cloud"` 映射为 worktree（见「子代理字段」）。需要云代理本体的步骤（如它的面板状态或它自己的机器）跳过。 |
| 内置 PR 工具 | 用步骤里给的 forge 命令，如 `gh pr create`。这不算跳过，不要写那一行。 |
