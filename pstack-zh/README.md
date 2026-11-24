# pstack

我是 [poteto](https://x.com/poteto)。我不是什么总裁或 CEO，但在 Meta、Netflix 和 Cursor 都跟几百万行级别的代码打过交道。我也在 React 核心团队，参与开发和维护 React Compiler。

现在越来越多人觉得 AI 写的 `slop` 代码太多了。我完全同意。我不想像带着二十个流水线水货写手那样出货。没有质量的吞吐量不是我要追求的目标。想走得快，得先扎得深。

**`pstack` 就是我的答案。** 这套 `skill` 正是我每天在 Cursor 里用来交付高质量代码的工具，它能把 Cursor 变成一支真正靠谱的工程团队。它的目标不是把代码行数拉满，恰恰相反，`pstack` 帮你写出更少、但质量更高的代码。

**`pstack` 让你敢于放心并行。** 当你能在一个代理身上扎得够深、信得过它能写出干净且经得起验证的代码，你才能真正放手并发。同时开多个挂着 `poteto-mode` 的代理，放心让它们按严谨的工程原则干活。

**Cursor 让你博采众长。** 每个前沿模型都有自己的长板和短板。用 `pstack` 可以搭配任何模型；事实上，我这里很多 `skill` 都内置了多模型协同流程，专门发挥各自的优势。

欢迎 fork、改进、改成顺手的样子，也欢迎提 PR。

## 安装

```bash
/add-plugin pstack
```

在 Claude Code 中安装：

```bash
/plugin marketplace add cursor/plugins
/plugin install pstack@cursor-plugins
```

Claude Code 对第三方 marketplace 默认关闭自动更新，所以 `pstack` 会停在你安装时的版本。要打开自动更新，运行 `/plugin`，切到 **marketplaces** 标签页，选中 `cursor-plugins`，然后选 **enable auto-update**。想手动更新一次，运行 `claude plugin update pstack@cursor-plugins`。

Claude Code 会给插件命令和子代理加上命名空间前缀，因此 `/poteto-mode` 在那里叫 `/pstack:poteto-mode`。其余 Cursor 专有名称的映射全写在 [Claude Code 适配说明](./docs/harness/claude-code.md) 里。在 Claude Code 里，`/pstack:setup-pstack` 会把你的模型配置写进 `~/.claude/rules/pstack-models.md`；遇到只有 Cursor 才有的能力（如 Bugbot 或 Automations），会输出一行跳过说明然后继续。

Claude Code 实际安装的是仓库根目录下 [`harness/pstack/`](https://github.com/cursor/plugins/tree/main/harness/pstack) 里生成的副本（包含本 README 和指南）。如果你改动了 `pstack`，记得在仓库根目录运行 `node scripts/generate-pstack-harness-trees.mjs` 并提交生成结果。生成副本过期时 CI 会报错。

## 快速上手

就两步：

1. 运行 [`/setup-pstack`](./skills/setup-pstack/SKILL.md)，选好推理预算，挑出各角色要用的模型。
2. 只要做任何需要严谨对待的工作，就用 [`/poteto-mode`](./skills/poteto-mode/SKILL.md)。

第一次用？[pstack 使用指南](./docs/guide/README.md) 会带你跑完第一个真实任务，从安装配置、写 `prompt` 一路讲到实跑验证和过夜挂机。卡住了或者拿不准该用哪个 `skill`，直接问 [`/poteto-help`](./skills/poteto-help/SKILL.md)。

就这么简单。其他 `skill` 都是按场景触发的，`poteto-mode` 会在步骤需要时自动替你调用。开箱默认下，写代码委派（`Feature`、`Refactoring`、`Bug fix`、`Perf issue`、`Hillclimb`）、文本写作和判断全部交给 `xhigh` 档位的 Opus 5.5，且任何角色都不超过 `xhigh`。多模型评审团之外，Fable 5.2 只在你明确点名或同一份 `brief` 用 Opus 5.5 连续两次失败后才启用。默认多模型评审团是 Fable 5.2 / Opus 5.5 / Gemini 4 Neon。任何一项都可以用 [`/setup-pstack`](./skills/setup-pstack/SKILL.md) 改掉。

## 用法

开工前先挂上 [`/poteto-mode`](./skills/poteto-mode/SKILL.md)。它会读你的需求，挑出匹配的 `playbook`，并在跑每一步时拉起需要的其他 `skill`。

输入任务前先从 `/` 菜单里点选 `/poteto-mode`，好让 Cursor 把这条 `skill` 挂到当前消息上。

### 直接用 [`/poteto-mode`](./skills/poteto-mode/SKILL.md) 就行

这是我最常用的主入口，只要需要代理严谨干活我就用它。里面内置了 22 个 `playbook`：

```
/poteto-mode 这个 PR 有个隐蔽 bug，空闲状态下每隔 750ms 滚动条就会自己漂移一下。先复现，再修复并验证。
```

```
/poteto-mode 我去睡了。就算 CI 偶发抖动，也要把这叠 PR 全合入主干，明早我要看到全部合并完。
```

<details>
<summary>全部 22 个 playbook</summary>

| playbook | 适用场景 |
|---|---|
| [Investigation](./skills/poteto-mode/playbooks/investigation.md) | 只读提问：X 是怎么工作的、Y 当初为什么这么设计、我们确定靠谱吗。 |
| [Bug fix](./skills/poteto-mode/playbooks/bug-fix.md) | 复现缺陷、定位根因，并用运行时证据修好。 |
| [Perf issue](./skills/poteto-mode/playbooks/perf-issue.md) | 追踪实测变慢的路径，对照基线优化。 |
| [Hillclimb](./skills/poteto-mode/playbooks/hillclimb.md) | 围绕单一量化指标向目标持续做科学迭代：循环提假设、测前后对比，确认正向收益才留一个 commit。 |
| [Runtime forensics](./skills/poteto-mode/playbooks/runtime-forensics.md) | 通过活进程打点插桩诊断运行时症状（内存泄漏、空闲 CPU 空转、界面卡顿）。 |
| [Trace forensics](./skills/poteto-mode/playbooks/trace-forensics.md) | 分析已抓取的性能产物（cpuprofile、trace、spindump、heap snapshot）。 |
| [Feature](./skills/poteto-mode/playbooks/feature.md) | 新增或改动功能行为，从先定好数据结构形状起步。 |
| [Refactoring](./skills/poteto-mode/playbooks/refactoring.md) | 保持外部行为不变的代码结构调整。 |
| [Prototype](./skills/poteto-mode/playbooks/prototype.md) | 低成本做用完即弃的草样原型，用来敲定设计或行为决策，或靠实跑观察裁决分叉。 |
| [Visual parity](./skills/poteto-mode/playbooks/visual-parity.md) | 两套实现之间的像素级 UI 等价对齐。 |
| [Authoring a skill](./skills/poteto-mode/playbooks/authoring-a-skill.md) | 编写或修改 `SKILL.md`。 |
| [Eval](./skills/poteto-mode/playbooks/eval.md) | 盲测某次 `skill` 或 `prompt` 改动对代理真实行为的影响。 |
| [Babysit](./skills/poteto-mode/playbooks/babysit.md) | 把单个 PR 或叠栈 PR 推到已就绪可合入状态：清冲突、处理评审评论、盯绿 CI。 |
| [Shipping](./skills/poteto-mode/playbooks/shipping.md) | 独立验证全绿 PR 栈，再把从栈底起连续验证通过的一段自下而上合入主干（默认 GitHub，本地有 Origin 时优先 Origin）。 |
| [Autonomous run](./skills/poteto-mode/playbooks/autonomous-run.md) | 盯住完成条件不停歇跑完长任务。 |
| [Autopilot-full](./skills/poteto-mode/playbooks/autopilot-full.md) | 一条独立 PR 队列从开发到合入全自主跑完，每个 PR 配一名主理代理。代码就绪后由 `swarm` 验明正身，后续补丁一有改动就重新验证。 |
| [Autopilot-stack](./skills/poteto-mode/playbooks/autopilot-stack.md) | 去掉合入动作的 `Autopilot-full`。造完并验完 PR 交给操作者审查合入，仅在确实存在依赖时叠栈。 |
| [Session pickup](./skills/poteto-mode/playbooks/session-pickup.md) | 断点续接或接管前任代理没干完的活。 |
| [Pause safely](./skills/poteto-mode/playbooks/pause-safely.md) | 体面挂起进行中的工作，留下干净现场供后续续接。 |
| [Multi-phase plan](./skills/poteto-mode/playbooks/multi-phase-plan.md) | 跨越多个阶段或叠栈 PR 的拆分方案。 |
| [Worktree cleanup](./skills/poteto-mode/playbooks/worktree-cleanup.md) | 按安全门禁审计并清理已合或废弃的 `worktree` 与过期 iOS 模拟器，回收磁盘空间。 |
| [Opening a PR](./skills/poteto-mode/playbooks/opening-a-pr.md) | 把改动整理成小步有序的 commit，写常规提交标题与简报式正文开出 PR。挂在其余所有 `playbook` 的最后执行。 |

</details>

调用后它会做三件事：

1. 把你的任务匹配到一个 [playbook](./skills/poteto-mode/playbooks/)，并开一张待办清单，最前面几项原样抄入该 `playbook` 的步骤。
2. 跑到对应步骤时，自动路由并调用其他 `skill`。
3. 按使用方和维护者的视角，写出不带 `slop` 的简洁回复。

完整的规则和 `playbook` 匹配表见 [`skills/poteto-mode/SKILL.md`](./skills/poteto-mode/SKILL.md)。

想让 [`/poteto-mode`](./skills/poteto-mode/SKILL.md) 在整个多轮对话里常驻生效，从 `/` 菜单选中它后按 Option+Enter（Mac）或 Alt+Enter（Windows），不要直接按回车。这样它会作为 [Custom Mode](https://cursor.com/docs/skills#using-a-skill-as-a-custom-mode) 挂载（Cursor 的 Agents 窗口和 CLI 均支持），在退出模式前每一轮都留在上下文里。直接按回车只会附着在当前这一条消息上。

[`/poteto-mode`](./skills/poteto-mode/SKILL.md) 和 Cursor 的 `/loop` 命令是绝配。你可以让 Cursor 连跑好几个小时，同时不丢掉工程严谨性。

## 全部 `skill`

下面大多数 `skill` 在步骤需要时都会由 [`/poteto-mode`](./skills/poteto-mode/SKILL.md) 自动拉起（`why`、`architect`、`arena`、`swarm`、`interrogate`、`unslop`、`no-comments`、`technical-writing`、`tdd` 以及 24 条 `principle`）。当你想单独调用某一个时，直接看下表：

```
/how 我们是怎么取消正在运行的任务的？查找待取消任务时有没有 N+1 查询？
```

```
/interrogate 审一下这个 PR。
```

<details>
<summary>全部 skill 清单</summary>

| skill | 什么时候用 |
|---|---|
| [`/poteto-mode`](./skills/poteto-mode/SKILL.md) | 任何非琐碎任务的默认总入口。 |
| [`/poteto-help`](./skills/poteto-help/SKILL.md) | 刚接触 `pstack`，或拿不准该用哪个 `skill`、`playbook`、`principle`。先弄清你要干嘛、针对性解答，再给你一条可直接发出去的 `prompt`。只有主动敲 `/poteto-help` 才会触发。 |
| [`/in-your-own-words`](./skills/in-your-own-words/SKILL.md) | 开工前先让代理用自己的话复述你的目标和要解决的问题。只有主动敲 `/in-your-own-words` 才会触发。 |
| [`/sharpen`](./skills/sharpen/SKILL.md) | 发 `prompt` 前想把要求挖得更深（但不扩大任务范围）：点出顶尖专家会多做什么、从哪份最原始的材料入手、用什么方法和工具，以及什么外部证据能证明结果正确。它会返回重写后的 `prompt`，要求对能靠实验定夺的分叉先做原型验证，产品与偏好选择仍留给你。它自己不动手干活，只有主动敲 `/sharpen` 才会触发。 |
| [`/reframe`](./skills/reframe/SKILL.md) | 说不清自己在做什么、因而没法向代理清晰提问时使用。直接从你的文件和原话出发；如果这段描述可能指向不止一个问题，先列出两到三种可能问题及区分信号并挑出最可能的一个。接着按对实现影响大小给出 8 到 12 个专业术语，每条对应到原话中的部分并附上亲自核验过链接的真实项目。再从 2 到 3 个用不同名字解决同类问题的邻近领域借词，讲清类比在何处失效，最后用新术语重写你的描述。只有主动敲 `/reframe` 才会触发。 |
| [`/how`](./skills/how/SKILL.md) | 想听资深工程师视角把某个子系统的运行机制讲透。 |
| [`/why`](./skills/why/SKILL.md) | 想知道某段代码当初为什么这么设计。只查历史记录不靠瞎猜：翻阅引入它的 commit、PR 讨论和后续历次变更，线索太薄时再往外查。严格引用原作者原话，标明哪些是推断，并直说哪些问题记录里没答案。 |
| [`/recall`](./skills/recall/SKILL.md) | 开新活或续接旧活前，从你自己的近期对话和团队共享记录里把某个话题的上下文拼回来，交给你一份精炼的现状 `brief`。 |
| [`/ketchup`](./skills/ketchup/SKILL.md) | 想用大白话和小图速览自你上一条消息以来这场对话里发生了什么，把所有等你拍板的事项列齐，保证只看这条回复就够做决定（哪怕因此篇幅变长）。 |
| [`/ketchup-video`](./skills/ketchup-video/SKILL.md) | 把 `/ketchup` 的进度同步做成一段带字幕的简短幻灯片视频，视频下方用文字附齐等你拍板的事项。 |
| [`/blast-radius`](./skills/blast-radius/SKILL.md) | 面对一个看似很小的改动，想查出它可能会把别处哪里搞坏，并找出让改动安全的那一条关键事实，靠实跑代码证明而不是光写分析报告。 |
| [`/architect`](./skills/architect/SKILL.md) | 准备写跨函数边界的代码前，先把调用方用法、类型签名和模块划分定下来。 |
| [`/arena`](./skills/arena/SKILL.md) | 想让 N 个并行代理同题做设计或写代码，选出基底再手工吸取各家最强的部分。 |
| [`/swarm`](./skills/swarm/SKILL.md) | 想让 N 个并行工人分片覆盖或同题赛马，最后收回一份紧凑汇总报告。 |
| [`/interrogate`](./skills/interrogate/SKILL.md) | 手头有份 `diff`，想让不同模型轮番去攻破它，只留下实跑验证过的问题条目。 |
| [`/automate-me`](./skills/automate-me/SKILL.md) | 想从你实际干活的历史记录里提炼出属于你自己的 `<你的名字>-mode` 技能。 |
| [`/make-bot-ui`](./skills/make-bot-ui/SKILL.md) | 想搭一个点按钮就能通过 webhook 唤醒 Grok Bot 的页面或面板，包含 sender key 安全托管和 Tailscale 暴露。 |
| [`/setup-pstack`](./skills/setup-pstack/SKILL.md) | 配置 `pstack` 每个角色用什么模型和推理预算。自动探测可用模型并写入配置规则。 |
| [`/reflect`](./skills/reflect/SKILL.md) | 一个长任务刚落地，想把踩过的坑和有效套路沉淀成对现有 `skill` 的具体修改。 |
| [`/correct`](./skills/correct/SKILL.md) | 老是在同类低级错误上反复纠正代理。挖掘历史里的重复错误类型，按能生效的最高层级根治（先架构，再类型/lint/CI，再测试，文档放最后），并维护一张「规则与强制执行机制对照表」。 |
| [`/teach`](./skills/teach/SKILL.md) | 不满足于看摘要，想真正搞懂一项改动或一个子系统。串联 `how` 和 `why`，一张图接一张图把逻辑讲透。 |
| [`/tdd`](./skills/tdd/SKILL.md) | 修 bug 且本地有便宜好跑的测试路径。先写必挂的失败测试，再写修复代码。 |
| [`/benchmark-checklist`](./skills/benchmark-checklist/SKILL.md) | 跑了压测或测出了提速/退步数字。在汇报或据此做决策前，逐项核查瓶颈、调优配置、报错、重复采样和端到端相关性。 |
| [`/no-comments`](./skills/no-comments/SKILL.md) | 送审前清掉废话注释：派 Comment Sicko 审查，处理采纳的整改项，并把注释里声称的约束编码进类型或检查。 |
| [`/typescript-best-practices`](./skills/typescript-best-practices/SKILL.md) | 读写 TypeScript 时使用，把 `Type System Discipline` 落到具体语法写法上。 |
| [`/figure-it-out`](./skills/figure-it-out/SKILL.md) | 内置 `playbook` 都不够贴合时，为当前任务现设计一套严谨、可审计的专属执行流程。 |
| [`/show-me-your-work`](./skills/show-me-your-work/SKILL.md) | 需要一份可事后审计的决策日志，把每一步选择和依据记进可提交的 TSV 文件。 |
| [`/create-verification-skill`](./skills/create-verification-skill/SKILL.md) | 项目还没有脚本化实跑验证手段时，为当前项目生成一套带 `Feature Map` 的本地验证 `skill`（不限语言和平台）。 |
| [`/maintain-verification-skill`](./skills/maintain-verification-skill/SKILL.md) | 项目的验证 `skill` 和 `Feature Map` 落后于最新代码时，并发读源码加跑一遍实测，最多开一个 PR 修正经实证的偏差。 |
| [`/create-formal-verification-skill`](./skills/create-formal-verification-skill/SKILL.md) | 普通测试测不到的并发竞争、重试、状态机、解析器或 unsafe 代码。挑合适的形式化工具验证关键不变量，并生成本地 `skill` 供后续改动复查。 |
| [`/maintain-formal-verification-skill`](./skills/maintain-formal-verification-skill/SKILL.md) | 被形式化验证覆盖的代码改过之后，同步更新模型、`harness` 或属性并重跑，明确指出失败到底是验证漂移还是代码真 bug。 |
| [`/statechart`](./skills/statechart/SKILL.md) | 负责行为定义的产品或设计师想直观看到系统行为而不是读规约。校验 TLA+ 模型，把用户视角画成 Mermaid 状态图，标出违背规则的状态并给出最短触发路径。 |
| [`/unslop`](./skills/unslop/SKILL.md) | 润色清理文字，删掉 AI 腔和废话套话。 |
| [`/bro`](./skills/bro/SKILL.md) | 想把上一条回复用毫无术语的大白话重说一遍。 |
| [`/technical-writing`](./skills/technical-writing/SKILL.md) | 四层技术文档写作标准（Diátaxis + Google 开发者风格 + STE + 全球英语），用于文档、RFC、README、PR 描述和 commit message。 |

</details>

### 常用示例

平时我基本只在任务开头敲 [`/poteto-mode`](./skills/poteto-mode/SKILL.md)，让它自己挑 `playbook`，其他 `skill` 跑到对应步骤时会自动触发。少数几个我会直接点名调用。

<details>
<summary>全部使用示例</summary>

```
Bug fix:           /poteto-mode 这个 PR 有个隐蔽 bug，空闲时每 750ms 滚动条会漂移一下。
                   先复现，再修复并验证。
Perf issue:        /poteto-mode 明明做了虚拟列表，大数据量还是卡一两秒才出。
                   抓个 CPU trace 告诉我慢在哪。
Feature:           /poteto-mode 在 feature flag 后面做个小功能，验证它真的能跑通。
Prototype:         /poteto-mode 给 markdown 渲染器做两个原型方便对比，
                   每个原型单派一个子代理。
Multi-phase:       /poteto-mode 把这些 skill 开源成独立插件。不能漏任何内部信息，
                   在临时目录里操作，先给我看依赖关系图。
Autonomous run:    /poteto-mode 我去睡了。就算 CI 抖动也要把这叠 PR 合完，明早要全合入。
Babysit:           /poteto-mode 看看 PR 123，还有什么没解决的吗？
Visual parity:     /poteto-mode 开了这个开关后行距太高了，第二张图才是对的。
                   先复现再修到完全一致。
Figure it out:     /poteto-mode 我先走开一会儿。把所有调用方从同步 store 迁到新异步 store，
                   保持行为完全一致，我回来时要能放心确认没出岔子。
how:               /how 我们是怎么取消运行的？查待取消列表时有没有 N+1 问题？
why:               /why 这个 feature flag 到现在还没全量打开？
architect:         设计一套高信噪比、无误报的打点方案。先 /architect 一下。
arena:             /arena 把我这段 prompt 原封不动丢进 arena，我想对比它们的方案和你的。
swarm:             /swarm 对 packages/ 下面每个包跑一遍它的 check.sh，一包一工人，汇总成一份报告。
interrogate:       /interrogate 审一下这个 PR。
tdd:               /tdd 实现修复
unslop:            把新改的文案过一遍 unslop，压紧一点。
reflect:           /reflect 刚才这轮太耗时了，把踩的坑总结进 skill，下次别再重蹈覆辙。
correct:           /correct
show-me-your-work: /show-me-your-work 记一份决策日志，我回来再审。
automate-me:       /automate-me
poteto-help:       /poteto-help 审这个分支我该用哪个 skill？
```

</details>

## `poteto-agent` 与 Comment Sicko 两个子代理

[`/poteto-mode`](./skills/poteto-mode/SKILL.md) 运行在收到这条命令的当前对话里。由这个主对话掌握 `playbook`、待办清单以及所有子代理的派发。

`pstack` 还附带了 [`subagent_type: "poteto-agent"`](./agents/poteto-agent.md)，专门用来包装流程里派出去干活的子代理。它开工前会通读整份 `poteto-mode`（包含内联的 24 条 `principle` 索引）。要是偷懒换成默认的 `generalPurpose`，就会漏读这些规则导致行为跑偏。注意不要派 `poteto-agent` 去跑 `playbook` 本身。

[`/poteto-mode`](./skills/poteto-mode/SKILL.md) 和 [`subagent_type: "poteto-agent"`](./agents/poteto-agent.md) 走的是同一套规范包装。

另外还附带了 [Comment Sicko](./agents/comment-sicko.md)，一个只读的注释审查代理，对应 `subagent_type: "comment-sicko"`。通常通过 [`/no-comments`](./skills/no-comments/SKILL.md) 间接拉起，不需要手动调用。

## 24 条 `principle`

一共 24 篇短小精悍的 `skill`，每篇只讲一条原则。`poteto-mode` 在正文里内联了它们的索引，开工前先扫一遍。把它们拆成独立文件，是为了让其他 `skill` 可以按名字精准引用，也方便索引直达每条原则的完整细则。

<details>
<summary>全部 24 条 principle</summary>

| principle | 分组 | 核心规则 |
|---|---|---|
| [Laziness Protocol](./skills/principle-laziness-protocol/SKILL.md) | core | 优先删代码，选择能解决问题的最小改动。 |
| [Foundational Thinking](./skills/principle-foundational-thinking/SKILL.md) | core | 写逻辑前先把核心类型、数据结构、脚手架与功能顺序、并发共享状态想清楚。数据结构定对了，下游代码自然水到渠成。 |
| [Redesign from First Principles](./skills/principle-redesign-from-first-principles/SKILL.md) | core | 把新需求当成第一天就存在的底层前提去重新设计，不要硬打补丁外挂上去。 |
| [Attack the Premise](./skills/principle-attack-the-premise/SKILL.md) | core | 基于同一前提的两种及以上修法都在同一关失败时，把这个前提写出来直接验证，别再默认它成立继续瞎修。 |
| [Subtract Before You Add](./skills/principle-subtract-before-you-add/SKILL.md) | core | 先清掉死代码、多余校验和无效桩引用，再在更干净的底座上动手。 |
| [Minimize Reader Load](./skills/principle-minimize-reader-load/SKILL.md) | core | 数清问题与答案之间隔了多少层、读者脑子里得记多少隐式状态；拍平单调用方套壳，收窄可变状态作用域。 |
| [Outcome-Oriented Execution](./skills/principle-outcome-oriented-execution/SKILL.md) | core | 带有明确阶段边界的计划内重写和迁移，直接向目标架构收敛，别用注定要删的兼容代码去粉饰中间态。 |
| [Experience First](./skills/principle-experience-first/SKILL.md) | core | 宁可多花功夫让用户爽，也不要图实现省事；宁可少做几个精品，不要端出一堆半成品。 |
| [Exhaust the Design Space](./skills/principle-exhaust-the-design-space/SKILL.md) | core | 动手定案前，做 2–3 个互相竞争的原型并排比一比。 |
| [Build the Lever](./skills/principle-build-the-lever/SKILL.md) | core | 不止批量活，任何非琐碎的修改、迁移、分析或检查，都该造出能执行或证明它的工具（codemod、脚本、生成器或供子代理遵守的 `skill`），别纯手搓。工具本身就是评审人可复跑的产物。 |
| [Model the Domain](./skills/principle-model-the-domain/SKILL.md) | architecture | 用明确的数据结构表达领域逻辑，不要散落一地条件分支。 |
| [Boundary Discipline](./skills/principle-boundary-discipline/SKILL.md) | architecture | 把校验防线集中在系统边界（CLI、配置、网络、外部 API），内部信任类型，业务逻辑写成纯函数。 |
| [Type System Discipline](./skills/principle-type-system-discipline/SKILL.md) | architecture | 让非法状态在类型上无法构造，用 Branded Types 区分语义基础类型，在边界解析外部数据，穷尽枚举变体，从权威 schema 派生类型。 |
| [Make Operations Idempotent](./skills/principle-make-operations-idempotent/SKILL.md) | architecture | 无论前面只跑了一半还是多次重试，最终都能收敛到同一个终态。 |
| [Migrate Callers Then Delete Legacy APIs](./skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | architecture | 同一轮里把所有调用方迁完并立刻删掉旧接口，不留兼容过渡层。 |
| [Separate Before Serializing Shared State](./skills/principle-separate-before-serializing-shared-state/SKILL.md) | architecture | 先把并发共享拆开消除；只有单一共享写者确实是业务不变量时，才在结构上加串行化。 |
| [Prove It Works](./skills/principle-prove-it-works/SKILL.md) | verification | 做完任务、宣布完成前，对着真实产物实跑验证（跑功能、读落库实值、审 `diff`），别拿表面指标、口头汇报或「能编译」交差。 |
| [Fix Root Causes](./skills/principle-fix-root-causes/SKILL.md) | verification | 把每个症状追回系统第一次走偏的地方去修。加防御判断只有在它处理的状态本身合法时才算真修复。 |
| [Sequence Work into Verifiable Units](./skills/principle-sequence-verifiable-units/SKILL.md) | verification | 适用于多步批量活及 commit/PR 叠栈。拆成每个都以可验证状态收尾的小单元，验完一个再干下一个，让交付顺序本身向评审人自证清白。 |
| [Test Behavior, Not Implementation](./skills/principle-test-behavior-not-implementation/SKILL.md) | verification | 写、改或保留测试时，只断言代码使用方能观察到的外部行为，确保行为坏了测试必挂、只改内部实现时测试依然通过。 |
| [Explain the Number](./skills/principle-explain-the-number/SKILL.md) | verification | 相信、汇报或依据任何自测数字（提速、退步、吞吐、延迟、eval）做决定前，先查明限制它的瓶颈，并排除它测到的压根不是你以为的那件事。 |
| [Guard the Context Window](./skills/principle-guard-the-context-window/SKILL.md) | delegation | 大块读取和重活丢给子代理，主线程只留精炼摘要，不塞原始大段输出。 |
| [Never Block on the Human](./skills/principle-never-block-on-the-human/SKILL.md) | delegation | 可撤回的活先干完把结果端出来，让人事后纠偏；确认环节只留给不可逆操作。 |
| [Encode Lessons in Structure](./skills/principle-encode-lessons-in-structure/SKILL.md) | meta | 把规则固化成 lint、元数据标记、运行时检查或脚本，不要一味往上堆文字提醒。 |

</details>

## 未随本包附带的内容

`poteto-mode` 引用了几个并不在本插件里的组件：

- `/deslop` 和 `deslop` `skill` 属于 `cursor-team-kit` 插件。
- `control-cli`（用于 CLI 和 TUI）与 `control-ui`（用于浏览器、Electron 和 Web）同样在 `cursor-team-kit` 里。
- `/create-skill` 是 Cursor 内置能力。Cursor 还内置了一个盯 PR 的 `/autopilot`；在 `poteto-mode` 里，查 PR 状态的请求会统一走 [Babysit playbook](./skills/poteto-mode/playbooks/babysit.md)。

想用完整套功能，把 `cursor-team-kit` 和 `pstack` 一起装上就行。

## 为什么没有专门的规划 `skill`？

Cursor 自带的 Plan Mode 已经很好用，跟 `pstack` 配合得很顺。不过就我个人而言，我不太迷信写纸面规划，最好的规格说明书就是代码本身。如果你确实需要出书面计划，[`/poteto-mode`](./skills/poteto-mode/SKILL.md) 里有对应 `playbook` 兜底，只是不设为默认动作。

## 改成你自己的风格

`poteto-mode` 是我的个人工作流，你未必想照单全收。

直接敲 [`/automate-me`](./skills/automate-me/SKILL.md)。它会翻你近期的对话记录，根据你平时真实的干活习惯起草一份 `<你的名字>-mode` `skill`，底层依然走 `pstack` 路由。你既保留了 `pstack` 的底座，又能拥有与 `poteto-mode` 并列的个人模式。

模型配置也全可定制。敲 [`/setup-pstack`](./skills/setup-pstack/SKILL.md)，它会探测你可用的模型，写一份简短的全局常驻规则，把每个角色（写代码、做判断、多模型评审团）映射到指定模型。每个 `skill` 都会读这份规则，没配时就退回合理的默认值，你只需要覆盖自己关心的项。

当上游默认模型更新时，之前写下的规则还会钉在旧默认值上，直到你重跑一次 `/setup-pstack`。重跑会自动替换它能识别出来的旧默认值，同时保留你手动改过的自定义角色。如果要清掉它识别不出的旧绑定，先把对应那一行或整个规则文件删掉就行。

## Automations

`pstack` 还附带了一套默认休眠的 [Benny 自动化包](./automations/benny/)。Benny 负责分诊 Slack 上的问题反馈，然后用真实 UI 证据复现并修复确认的 bug。它的文件不会注册成斜杠 `skill`。

要启用它，让 Cursor 读 [`FOR_AGENTS.md`](./automations/benny/FOR_AGENTS.md)。初始化脚本会把整套文件拷进目标仓库的 `.cursor/automations/benny/`，开启 `pstack` 共享技能，并把用户配置独立放在外面。Benny 依赖 Cursor Automations 运行时，因此仅限 Cursor 使用。

## 许可

MIT
