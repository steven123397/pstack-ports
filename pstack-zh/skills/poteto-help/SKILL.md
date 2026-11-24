---
name: poteto-help
description: 引导用户完成 pstack 配置、上手 /poteto-mode，以及按场景挑选合适的 skill、playbook 或 principle。带着问题输入 /poteto-help 触发。
disable-model-invocation: true
---

# Poteto help

直接回答用户关于 `pstack` 的问题，给对方一条现成能发的 `prompt`，并附上答案出处对应的文件链接。遇到咨询类问题时不要直接替用户开工：用户问的是怎么用，而跑一轮 `pstack` 要消耗实打实的 token，应该把决定权和 `prompt` 交回给用户自己发。

如果用户发的是直接干活的请求（比如「用 pstack 修一下这个 bug」），这就不算帮助提问。此时直接读取 [`poteto-mode`](../poteto-mode/SKILL.md)，按它的流程开工，并顺口提醒一次开 Custom Mode 可以让它每轮常驻。

本文件负责把问题映射到真正掌握细节的 `skill` 和指南页面，具体细节以那些文件为准。引用前先读目标文件，如果本索引和目标文件有出入，以目标文件为准。这里的相对链接指向本地插件目录，用户未必点得开，因此发给用户时附上公开地址：`https://github.com/cursor/plugins/blob/main/pstack/` 拼上对应相对路径。

## 先摸清用户需要什么

根据用户的提问和当前对话推断需求。如果场景已经很明确（比如「审 PR 该用哪个 skill？」），直接跳到对应小节作答。如果还是拿不准，提一个单选题列出下面五个选项，只回答对方选的那一块：

- 完成安装与初始配置
- 用 `/poteto-mode` 开始一个任务
- 按场景挑一个合适的 `skill`
- 排查跑偏或出问题的运行
- 定制成我自己的 `pstack`

检查会影响回答的本地状态，且只在确实影响结论时才提：

- 没有 `~/.cursor/rules/pstack-models.mdc`，说明用户还没跑过 `/setup-pstack`，所有角色都会走默认模型。
- 项目里没有 `verify-*` skill 或其他应用测试 `harness`，说明代理没有脚本化驱动应用的手段。当问题涉及证明改动生效时，提一下 `/create-verification-skill`。
- 项目里没有形式化验证 `skill`，说明超出单测覆盖范围的属性还没验证手段。当问题涉及并发竞争、不变量或单测极难撞到的边界时，提一下 `/create-formal-verification-skill`。如果项目里已经有形式化验证 `skill`，且它覆盖的代码在上次同步记录的 commit 之后发生过变更，当问题碰到这块代码时提醒跑 `/maintain-formal-verification-skill`。

如果缺少模型规则文件且这件事当前有影响（用户是新手、问到了配置或成本，或者答案依赖具体跑哪些模型），问一句现在要不要为各角色选好模型和推理预算。每次对话最多问一次。如果用户需求本身也不清楚，把两个问题合在一起问。提供两个选项：

- 现在配：给对方 `/setup-pstack` 去敲，同时正常回答他们原本的问题。
- 以后再说：正常回答问题，顺带补一句「跑 `/setup-pstack` 之前，所有角色都会用默认模型」。

## 完成安装与初始配置

1. 在对话框里敲 `/add-plugin pstack` 安装，或从侧边栏 Customize 里添加。
2. 运行 [`/setup-pstack`](../setup-pstack/SKILL.md)。它会问你推理预算、为每个角色配好模型并写入规则文件（对新开对话生效）。接着如果项目里还没有，它会各问一次要不要生成验证 `skill` 和形式化验证 `skill`。
3. 带上一个目标和一个能判通过/失败的完成标准，用 `/poteto-mode` 跑一个真实任务。

装上插件后，在你主动调用之前不会改变任何行为。只有 `/setup-pstack` 会根据用户的自然语言自动加载。完整说明见 [README](../../README.md) 和 [指南第 1 篇](../../docs/guide/01-setup.md)。可以顺手帮用户把第一条 `prompt` 组织好，写法参考 [`references/prompting.md`](references/prompting.md)。

如果用户担心成本，直接讲清楚 token 花在哪、怎么省：`pstack` 多花的 token 主要在子代理和多模型评审团上。重跑 `/setup-pstack` 选低一档预算或便宜点的模型即可。把角色设为 `auto` 或 `inherit-parent` 会沿用主对话模型，主对话开 Auto 或用便宜模型时很省钱。缩短评审团列表能直接减少并行子代理数（列表里每项开一个）。把 `/poteto-mode` 留给真正需要严谨对待的活。

`pstack` 面向 Cursor 构建，但也支持在 Claude Code 里安装：先 `/plugin marketplace add cursor/plugins`，再 `/plugin install pstack@cursor-plugins`。在 Claude Code 里所有命令带 `pstack:` 前缀（如 `/pstack:poteto-mode`），具体名称映射见 [Claude Code 适配说明](../../docs/harness/claude-code.md)，遇到 Bugbot 或 Automations 这类 Cursor 专属能力时会输出一行跳过说明后继续。

其他支持 Agent Skills 格式的工具也能读取这些 `skill` 文件。不过大多数工作流 `skill`（包括 `/poteto-mode`、`/how` 和 `/teach`）需要派生 Cursor 子代理（部分带按角色指定的模型），而且 Custom Mode 和 `/loop` 属于 Cursor 特性，因此这些部分在别的工具里可能跑不通。

## 用 `/poteto-mode` 开始一个任务

`/poteto-mode` 会把任务匹配到一个 `playbook`，把步骤原样抄进待办清单，跑到对应步骤时自动调起其他 `skill`。好 `prompt` 只写清目标和验收标准，不手列一串 `skill`（人手排顺序反而容易打乱或漏步）。帮用户措辞前先读 [`references/prompting.md`](references/prompting.md)，更多示例看 [指南第 2 篇](../../docs/guide/02-poteto-mode.md)。

`/poteto-mode` 能不能跨轮常驻，取决于怎么启动它：

- 选中 `/poteto-mode` 直接按回车，只附着在当前这一条消息上，聊几轮就淡出了。
- 按 Option+Enter（Mac）或 Alt+Enter（Windows），或者在技能条目上选 Use as Mode，会把它设为 Custom Mode。退出模式前每一轮都在上下文里，又不干扰普通闲聊对话。
- Cursor 官方文档说明 Custom Mode 支持 Agents 窗口和 CLI。在其他界面里，每次开新任务时手动带 `/poteto-mode` 即可。

聊到这一块时附上 [Cursor skills 文档](https://cursor.com/docs/skills) 链接。长对话中途切话题时，加一句「新任务（new task）」让模式重新匹配新 `playbook`。`/poteto-mode` 跑 `playbook` 步骤派出的子代理默认就是 `poteto-agent`；如果想让自己手动派的子代理也套用同款风格，派生时指定 `subagent_type: "poteto-agent"`。

## 按场景挑选 `skill`

默认答案永远是 `/poteto-mode`，它会在步骤需要时自动拉起其余大多数 `skill`。只有当用户明确想比默认 `playbook` 多做或少做某一环时，才直接点名某个 `skill`。推荐之前先读那个 `skill` 的正文，并给一条示例 `prompt`。

| 用户想要 | 对应 skill |
|---|---|
| 严谨完成任何非琐碎任务 | [`/poteto-mode`](../poteto-mode/SKILL.md) |
| 开工前先核对代理有没有听懂自己的目标和问题 | [`/in-your-own-words`](../in-your-own-words/SKILL.md) |
| 发 `prompt` 前把它改得更深入（但不扩大任务范围）：补上顶尖专家会多做的事、原始材料、方法工具和外部客观校验；只交回重写后的 `prompt`，不直接干活 | [`/sharpen`](../sharpen/SKILL.md) |
| 学习自己正在构建之物的专业术语（含从邻近领域借来的词，每条引用出处都经核实），并用新术语重写需求描述 | [`/reframe`](../reframe/SKILL.md) |
| 搞懂现有代码怎么运作，或者新代码该放哪一层 | [`/how`](../how/SKILL.md) |
| 查清代码当初为什么这么设计，或者某个数字从哪来的 | [`/why`](../why/SKILL.md) |
| 用大白话彻底搞懂一项改动或一个子系统 | [`/teach`](../teach/SKILL.md) |
| 拼回自己最近在某个话题上的工作上下文 | [`/recall`](../recall/SKILL.md) |
| 用大白话和小图同步自上一条消息以来这场对话发生了什么，把等你拍板的事项列齐到光看回复就能决策 | [`/ketchup`](../ketchup/SKILL.md) |
| 把 `/ketchup` 做成带字幕的简短幻灯片视频，视频下面用文字列出待拍板事项 | [`/ketchup-video`](../ketchup-video/SKILL.md) |
| 查一个小 `diff` 可能会把外部哪里搞坏，并实跑证明安全 | [`/blast-radius`](../blast-radius/SKILL.md) |
| 写跨函数边界代码前先把类型和模块形状定好 | [`/architect`](../architect/SKILL.md) |
| 拿同一份 `brief` 并行跑几套方案，再取长补短合成最优版 | [`/arena`](../arena/SKILL.md) |
| 用云端代理并行跑分片检查或赛马，收一份汇总报告 | [`/swarm`](../swarm/SKILL.md) |
| 让不同模型对抗审查一份 `diff`，试着把它跑崩 | [`/interrogate`](../interrogate/SKILL.md) |
| 本地有便宜单测时，先写必挂测试再修 bug | [`/tdd`](../tdd/SKILL.md) |
| 改 `.ts` 或 `.tsx` 代码时套用 TypeScript 类型规范 | [`/typescript-best-practices`](../typescript-best-practices/SKILL.md) |
| 送审前交给没写这段代码的审查员清理废话注释 | [`/no-comments`](../no-comments/SKILL.md) |
| 清理文章或回复里的 AI 套话 | [`/unslop`](../unslop/SKILL.md) |
| 按严格标准撰写或审校文档、RFC、README、PR 描述或 commit message | [`/technical-writing`](../technical-writing/SKILL.md) |
| 把上一条晦涩回复翻译成大白话 | [`/bro`](../bro/SKILL.md) |
| 给项目生成一套可脚本化驱动应用、验证行为的本地 `skill` | [`/create-verification-skill`](../create-verification-skill/SKILL.md) |
| 校准项目验证 `skill` 和 `Feature Map`，让它们重新跟上最新代码 | [`/maintain-verification-skill`](../maintain-verification-skill/SKILL.md) |
| 对并发竞争、不变量或单测极难触达的属性做形式化验证 | [`/create-formal-verification-skill`](../create-formal-verification-skill/SKILL.md) |
| 受验证代码改动后同步更新形式化验证，判断失败是验证漂移还是代码真 bug | [`/maintain-formal-verification-skill`](../maintain-formal-verification-skill/SKILL.md) |
| 用 TLA+ 校验过的状态图向产品或设计师直观展示用户视角行为，标出违背规则的最短路径 | [`/statechart`](../statechart/SKILL.md) |
| 汇报或依据性能实测数字行动前逐项核查真伪 | [`/benchmark-checklist`](../benchmark-checklist/SKILL.md) |
| 处理体量庞大、跨切面极广或需要走开后回来验收的复杂任务 | [`/figure-it-out`](../figure-it-out/SKILL.md) |
| 在长任务中持续记决策日志，事后做审计复盘 | [`/show-me-your-work`](../show-me-your-work/SKILL.md) |
| 为各角色挑模型并设置推理预算 | [`/setup-pstack`](../setup-pstack/SKILL.md) |
| 把自己的日常干活习惯提炼成个人专属 mode `skill` | [`/automate-me`](../automate-me/SKILL.md) |
| 把刚落地任务的经验教训沉淀成对现有 `skill` 的具体修改 | [`/reflect`](../reflect/SKILL.md) |
| 根治代理在仓库里反复犯的同类错误 | [`/correct`](../correct/SKILL.md) |
| 搭一个点按钮就能通过 webhook 唤醒 Grok Bot 的面板页面 | [`/make-bot-ui`](../make-bot-ui/SKILL.md) |
| 摸清 `pstack` 怎么用、该挑哪个工具 | `/poteto-help` |

如果同级目录下多出了上表没收录的新 `skill`，读它的 frontmatter 按 `description` 路由。`principle-*` 目录见下面的 `playbook` 与 `principle` 一节。

容易混淆的几组对照：

- `/how` 讲代码现在怎么跑，`/why` 讲当初为什么这么写，`/teach` 跑其中一个或两个再给你讲透。
- `/arena` 让所有工人拿同一份 `brief` 比拼，选基底再嫁接优点；`/swarm` 拆片覆盖或赛马，汇总成一份报告。
- `/interrogate` 审的是当前 `diff` 本身；`/blast-radius` 查的是 `diff` 之外可能被波及的地方，并实跑证明安全前提。
- `/recall` 跨近期多次对话拼上下文；`/ketchup` 只覆盖当前对话自你上一条消息以来的变化；接手某一场具体对话或分支走 `Session pickup` playbook。
- `/figure-it-out` 用来定制单次严谨长跑；`Autonomous run` playbook 负责把单个任务盯死完成条件一路跑完。

不在 `pstack` 本包里的项：

- `/deslop`、`control-cli` 和 `control-ui` 来自 `cursor-team-kit` 插件。
- `/loop` 和 `/create-skill` 是 Cursor 内置功能。
- `pstack` 没有 `/orchestrate` 这个斜杠 `skill`。如果 `/` 菜单里冒出 `/orchestrate`，那是别的插件提供的。

## `playbook` 和 `principle`

`playbook` 是 `/poteto-mode` 内部的步骤清单，不是独立 `skill`，所以没有单独的斜杠命令。在 `/poteto-mode` 里直接描述任务就能自动匹配，下面这些常见说法也会直接命中对应 `playbook`：

- 「babysit this pr」「盯一下这个 PR」或「看看 PR 123」→ `Babysit`。它把 PR 推到就绪可合入就停手，除非用户明确说要 merge、land 或 ship，绝不擅自合入。
- 「land the stack」「把这叠 PR 合入主干」→ `Shipping`。
- 「take over this branch」「接手这个分支」→ `Session pickup`。
- 「pause safely」「安全暂停」→ `Pause safely`。
- 「full autopilot on this queue」「这条队列跑全自动」→ `Autopilot-full`；「autopilot, don't merge」「全自动但别合」→ `Autopilot-stack`。
- 「run the eval playbook」「跑一遍 eval playbook」→ `Eval`。

不挂 `/poteto-mode` 直接说「babysit this pr」时，可能会误触发 Cursor 自带的同名技能。全部 `playbook` 列在 [`poteto-mode`](../poteto-mode/SKILL.md) 的 Playbooks 一节；开 PR、盯盘和合入的完整流程见 [指南第 6 篇](../../docs/guide/06-verify-and-ship.md)。

`pstack` 没有专门的规划 `skill`，Cursor 自带的 Plan Mode 跟它配合得很好。遇到跨阶段或叠栈 PR 的任务，让 `/poteto-mode` 出计划会命中 [Multi-phase plan playbook](../poteto-mode/playbooks/multi-phase-plan.md)，它只交付计划不直接写代码。如果是设计分叉，先用 `Prototype` playbook 或 `/architect` 在代码里敲定。

`principle` 是一条原则一篇的短 `skill`，`/poteto-mode` 会自动读它们并在回复里引用。平时很少手动触发，而是直接点名字纠偏，比如「按 Prove It Works 来，给我看真实输出」。想按需单独加载某一条时，敲 `/principle-<name>` 依然管用。全部 24 条见 [指南第 8 篇](../../docs/guide/08-principles.md)。

## 排查跑偏或出问题的运行

| 症状 | 解决办法 |
|---|---|
| 聊了几轮后模式不再起作用 | 当初是直接按回车启动的。改用 Custom Mode 常驻，或者每个新任务开头重敲 `/poteto-mode`。 |
| 问了个新问题却被当成上个任务的下一步 | 开头加一句「新任务（new task）」，或者直说这轮不需要走模式。 |
| 改完模型配置没生效 | `/setup-pstack` 写的规则只对新会话生效，重开一个对话。 |
| 花费的 token 比预期多 | 看上文「完成安装与初始配置」里的成本控制段落。 |
| 某个 `skill` 没自己触发加载 | 只有 `/setup-pstack` 会靠自然语言自动加载；其他 `skill` 都要手动敲命令或由 `/poteto-mode` 按需拉起，且它不会全量调用。 |
| 多个并行代理互相覆盖文件 | 给每个代理单开独立 `worktree`，或直接派成各自独占虚拟机的云端代理。 |
| 过夜循环忙活了一晚啥也没做完 | `/loop` 需要一个能判通过/失败的硬条件，不能给时长。详见 [指南第 7 篇](../../docs/guide/07-overnight.md)。 |
| 代理看编译变绿就宣布完工 | 直接要真实命令输出、应用操作流、落库实值或 profile，这就是 `Prove It Works` 原则。 |

中途任务跑偏时，[`references/prompting.md`](references/prompting.md) 里有现成的一句话纠偏模板；更多踩坑和实用 `prompt` 看 [指南第 10 篇](../../docs/guide/10-recipes-and-pitfalls.md)。

## 定制成你自己的 `pstack`

- [`/automate-me`](../automate-me/SKILL.md) 从你的近期历史记录起草个人专属 mode `skill`，与 `/poteto-mode` 并列使用。
- 任务结束后跑 [`/reflect`](../reflect/SKILL.md)，把经验教训变成经你批准的 `skill` 改动。
- `/poteto-mode 给 <某工作流> 写一个 skill` 会跑编写 `skill` 的标准 `playbook`；改完后用 `Eval` playbook 做盲测验证。
- 发现 `skill` 抽风，单开一个 PR 修它，别夹杂在当前业务功能里改。

以上几项都在 [指南第 9 篇](../../docs/guide/09-make-it-yours.md) 里详细展开。

## 回复要求

开门见山先给答案。最多附一个代码块里的示例 `prompt`（有合适模板时从 [`references/recipes.md`](references/recipes.md) 改写），再贴上出处文件的公开链接。除非用户主动要看全景地图，否则回答务必简短。
