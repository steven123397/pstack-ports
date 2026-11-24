# 安装与配置

这一页带你装好插件、选好 `pstack` 各角色使用的模型，然后跑通第一个任务。整套配置只需要一条命令加几句简短对话。

## 安装插件

在 Cursor 对话框里运行：

```text
/add-plugin pstack
```

Cursor 会提示插件安装成功。

如果在 Claude Code 里用，先运行 `/plugin marketplace add cursor/plugins`，再运行 `/plugin install pstack@cursor-plugins`。Claude Code 会给插件命令加 `pstack:` 前缀，因此本指南里所有命令在那里都要带上前缀，比如 `/pstack:setup-pstack`，它会把模型规则写到 `~/.claude/rules/pstack-models.md`。其他平台差异见 [Claude Code 适配说明](../harness/claude-code.md)。

## 挑选各角色模型

运行：

```text
/setup-pstack
```

[`/setup-pstack`](../../skills/setup-pstack/SKILL.md) 会探测你当前账号可用的模型，问你想要哪一档推理预算，把各个角色（写代码委派、判断评审、多模型评审团）列出来供你挑选。按提示答完后，它会写出一份 `~/.cursor/rules/pstack-models.mdc`，所有 `pstack` skill 都会读取这条规则。

开箱默认配置等价于 `large` 预算。代码、写作与判断跑在 `xhigh` 档位的 Opus 5.5 上，多模型评审团和 `swarm workers` 跑在 `high` 档位，任何角色都不超过 `xhigh`。多模型评审团之外，Fable 5.2 只在你为当前任务点名或同一份 `brief` 用 Opus 5.5 连续两次未通过验证后才启用。选 `medium` 全体降一档，`small` 降两档，这两档消耗的 token 都更少。

你只需要覆盖自己关心的角色。规则文件里没写的角色会自动沿用 `skill` 默认值；想恢复某个角色的默认设置，删掉那一行就行。重跑 `/setup-pstack` 会保留你手动改过的自定义角色。当上游默认模型调整时，旧规则文件里还会钉着老默认值，直到你重跑 `/setup-pstack`；重跑会自动把能认出的旧默认值换成新默认、告诉你替换了哪些，并保留你的其他自选项。想清掉它认不出的旧绑定，先把对应那一行或整个文件删掉。

如果你平时习惯用 Auto 模式，把对应角色设为 `inherit-parent` 或 `auto` 就行。这时 `pstack` 调用子代理时会省略 `model` 字段，让子代理直接继承主对话的模型。这两个值意思完全一样，都不是模型 `slug`。评审团角色对应的值是一个列表，列表里每写一项就会多开一个子代理，所以列表长度直接决定评审团人数。配置里还会设好 `swarm workers`，它是 `/swarm` 所有工人的默认模型（除非赛马模式显式为每一路指定了不同模型）。

## 要不要顺手生成验证 `skill`

配置快结束时，`/setup-pstack` 会检查你当前项目里有没有办法实跑验证应用行为（比如现成的 `verify-*` skill 或其他测试 `harness`）。如果都没有，它会问你一次要不要用 [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md) 自动生成一份。

选要，它会在 `.cursor/skills/verify-<app>/` 写出一套项目本地 `skill`，教代理怎么像真实用户那样操作你的应用，并在交给你之前先实跑验证一遍确认这套 `skill` 自己能跑通。选不要，配置就直接往下走，以后随时可以手动跑 `/create-verification-skill`。详细用法见 [实跑验证与合入 PR](./06-verify-and-ship.md)。

如果你刚上手 `pstack`，强烈建议选「要」。能自己验证结果的代理会一直修到检查通过为止；不能自己验证的代理，每次改完都得交回你手里肉眼排查。整份指南里，投入产出比最高的就是这套验证 `skill`。

接着，如果项目里还没有形式化验证 `skill`，配置流程还会问你一次要不要用 [`/create-formal-verification-skill`](../../skills/create-formal-verification-skill/SKILL.md) 生成一份。普通单测只测得到人想出来的用例，而形式化验证 `skill` 会在划定范围内穷尽检查某条关键属性（比如「同一个任务绝不会同时跑两份」）。如果你的代码涉及并发、重试、状态机或解析器，且一旦出 bug 代价很大又很难靠单测撞出来，就选「要」；否则先选「不要」，等以后需要了再补跑。详细说明见 [实跑验证与合入 PR](./06-verify-and-ship.md)。

全部配完后，记得新开一个对话窗口，模型规则只对新会话生效。

## 控制好 token 成本

`pstack` 会在子代理和多模型评审团上多花不少 token，这是换取严谨性的代价。想省着点花，可以这么调：

- 重跑 `/setup-pstack`，选低一档推理预算或更便宜的模型。主对话用强模型、写代码角色配便宜快的模型，是很划算的组合。
- 把部分角色设为 `auto` 或 `inherit-parent`，让它直接跟着主对话模型走。
- 缩短评审团模型列表，每少一项就少开一个子代理。
- 把 `/poteto-mode` 留给真正需要严谨把关的任务，一眼看穿的小修改没必要杀鸡用牛刀。

## 跑通你的第一个任务

挑一个真实但不大的小需求，像跟同事口头交代那样发出去：

```text
/poteto-mode 给这个命令加一个 --json 参数。普通文本输出要保持逐字节不变。两种格式都验证一遍。
```

留意看待办清单。排在最前面的几项就是自动匹配到的 `playbook` 步骤（这条 `prompt` 会命中 `Feature` playbook）。

之后正常接着聊就行。想让 `/poteto-mode` 在整场对话里一直生效，从 `/` 菜单选中它后按 Option+Enter（Mac）或 Alt+Enter（Windows），不要直接按回车。这样它会变成 [Custom Mode](https://cursor.com/docs/skills#using-a-skill-as-a-custom-mode)，在退出前每一轮都在上下文里（Agents 窗口和 CLI 均支持）。普通回车只会把它挂在当前这一条消息上，聊几轮就淡出上下文了。

下一篇：[用 `/poteto-mode` 统领任务](./02-poteto-mode.md)。
