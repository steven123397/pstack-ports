---
name: reflect
description: "针对当前活跃对话记录并行派发三位复盘审查子代理，提炼长效教训，并把每条教训精准路由成对现有 skill 的具体修改。在用户说 reflect 或「复盘一下」时适用。"
disable-model-invocation: true
---

# Reflect

从当前对话里挖掘长效经验教训，并落地成对 `skill` 的具体修改。

当用户说「reflect」「`/reflect`」或要求复盘本次对话时调用。如果对话本身琐碎、跑题，或者父会话已经按现有 `skill` 正确执行到位，直接跳过。一次性偶发事件不算长效教训。

## 1. 定位当前活跃的对话记录

扇出前，在系统提示词指定的 `agent-transcripts/` 目录里找到本段对话的 transcript 文件。绝不要用通配符横扫 `~/.cursor/projects/*/`，那样会越过工作区边界读到无关项目的私密对话。

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

这条命令同时覆盖旧版平铺结构（`<id>.jsonl`）、新版嵌套结构（`<id>/<id>.jsonl`）和子代理记录（`<parent>/subagents/<child>.jsonl`）。逐个读取候选文件的第一行 JSONL，挑出 `message.content[0].text` 包含本次对话开篇用户 `prompt` 的那个文件。如果都匹配不上，改传一份精炼的本次会话摘要。

## 2. 并行派发三位复盘审查子代理

在单条消息里发起三个 `Task` 调用，均为 `subagent_type: generalPurpose`、agent 模式（`readonly: false`）。审查子代理需要 MCP 权限去查 transcript 里提到的工单、聊天串和可观测性 trace，而 `readonly` 会剥离 MCP 权限。

每位审查子代理和综合整理者都对应 `pstack-models.mdc` 规则里的一行角色配置及默认值。把 `model` 设为对应行的值；如果规则文件或该行缺失，就用默认值。值为 `auto` 或 `inherit-parent` 时留空不传 `model`。如果 `Task` 工具拒绝了某个 `slug`，改用默认值并说明；连默认值也被拒，就从报错信息里挑同家族最接近的合法 `slug`。按 **poteto-mode** `skill` 的 Subagents 章节，为每个子代理选定匹配的推理档位与 fast/standard 速度。

| 审查视角 | 角色配置行 | 默认 `model` | `prompt` 模板 |
|---|---|---|---|
| 判断视角（Judgment） | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/judgment-reviewer.md` |
| 工具视角（Tooling） | `reflect tooling` | `claude-opus-5-5-high-fast` | `references/tooling-reviewer.md` |
| 逆向盲区视角（Divergent） | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/divergent-reviewer.md` |

把每份模板原样传入，只替换标记处的 transcript 路径或会话摘要。审查子代理直接在 `Task` 回复正文里交回发现。

## 3. 综合裁定

发起一次 `Task` 调用，`subagent_type: generalPurpose`，`model` 取自 `reflect judgment, divergent, synthesizer` 行（默认 `claude-opus-5-5-xhigh`），agent 模式（`readonly: false`），因为它同样需要通过 MCP 抽检引用出处。把 `references/synthesizer.md` 原样传入，并在占位符处内联三位审查子代理的完整输出。它会返回一份 `Accepted / Rejected / Backlog` 清单。

## 4. 结构化固化筛查

把 `Accepted` 列表里任何更适合用 lint 规则、脚本、元信息标记或运行时检查来兜底的条目，挪到 `Backlog`。参见 **encode-lessons-in-structure** `principle` `skill`。

## 5. 等待审批并落地

把综合裁定者给出的完整 `Accepted / Rejected / Backlog` 输出原样展示给用户，在拿到明确批准前绝不动手应用任何一条 `Accepted` 修改。由用户挑选子集，用户也可以改写路由目标。`skill` 改动会影响团队后续所有代理，绝不要自动应用。

`Backlog` 里的每一条无需等待批准，直接提进团队的 devex 或 backlog 追踪系统。只有 `Accepted` 清单需要等批准。

绝不要直接修改 `plugins/cache/` 下的 `skill`。提请审批前，先写明落地目标目录是 `.cursor/skills/<skill>/` 还是 `~/.cursor/skills/<skill>/`；获批后把对应 `skill` 目录拷贝到目标位置再改副本。绝不要顺手开 PR 或 `git push`。

严格按每条获批记录的 `Routing` 执行：

- 现有 `skill` 的琐碎微调（加一行要点、收紧一句话、修正过时事实）：由父会话直接改。
- 现有 `skill` 的实质改动（新增章节、新增模式表、改动超过约 10 行）：交给 Cursor 内置的 `create-skill` `skill`，走它的起草 / 测试 / 迭代循环。
- `tune description: <skill path>`（`skill` 本来就在，但该触发时没触发）：交给 `create-skill`，走它的 `description` 优化循环。
- `new skill via create-skill: <kebab-name>`：把新建任务交给 `create-skill`，绝不要临场随手拼凑结构。

如果当前环境自带 `SKILL.md` 校验器，宣布完成前对每一个动过的 `skill` 都跑一遍校验。

## 6. 给用户的收尾摘要

简短列清单，不要写开场废话：

- 已落地的修改：`<skill path>`，每条一句话说清改了什么。
- 新建的 `skill`：`<skill path>`，每条一句话（少见）。
- 已提进 devex 追踪系统的 `Backlog`：`<工单标题>`（`<标签>`），每条一句话。
- 已驳回项：每条写明被拒的发现及综合裁定者给出的理由。
