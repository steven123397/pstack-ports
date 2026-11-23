# 改成你自己的工作流

`poteto-mode` 只是一个人的工作习惯。它底层的 `playbook`、路由逻辑和模型角色分工，换成你的风格一样好使。这一页讲怎么生成个人专属模式、复盘沉淀会话经验、改造仓库让代理不再犯同类错、写出高质量的专项 `skill`，以及怎么在信任改动前做盲测 `eval`。

起步要比你想象的更小。第一天根本用不着配齐几十个 `skill`，甚至不用把整套插件全用上。先用大白话正常派活，观察代理总在哪里翻车；同一个坑踩到第二次，再补一条 `skill` 或一道检查。

## 用 `/automate-me` 生成你的个人模式

```text
/automate-me
```

你不需要自己绞尽脑汁总结个人风格，[`/automate-me`](../../skills/automate-me/SKILL.md) 会直接从你的历史记录里挖出来。它会扫描当前工作区里你近期的对话记录，提炼你在回复风格、派工习惯、验证标准、代码口味、行文和流程上的高频偏好，然后向你核实哪些真的代表你。确认后，它通过 Cursor 内置的 `create-skill` 起草 `.cursor/skills/<your-name>-mode/SKILL.md`，用 [`/unslop`](../../skills/unslop/SKILL.md) 过一遍文案，再从 `worktree` 开出一个 PR，让你像审普通代码那样审查它。

过阵子习惯变了，重跑一遍就行：

```text
/automate-me 用上次改完之后的新记录更新我的 mode skill
```

更新模式只挖掘上次改动之后的新对话。你没推翻过的旧规矩原样保留，有新证据的条目就修订，只在冒出全新习惯时才加新章节。

## 用 `/reflect` 把单次任务的教训写进 `skill`

刚跑完一个让你学到东西的任务，趁热打铁跑一句：

```text
/reflect 刚才这轮耗太久了，把学到的教训收进 skill，下次别再重复踩坑。
```

[`/reflect`](../../skills/reflect/SKILL.md) 会把当前对话记录发给三个并行审查代理，再由汇总代理把提议分进 `Accepted`、`Rejected` 和 `Backlog` 三类，等你拍板后再改任何 `skill`。只有真正能改变未来决策的提议才值得批。某一次偶发的离奇遭遇只是个案，不配升级成永久规则。

## 用 `/correct` 从仓库环境里根治反复犯的错

如果你发现自己在同一个错误上反复纠正代理，那就该改仓库本身，而不是寄希望于下次在 `prompt` 里多嘱咐两句。按拦截可靠度从高到低排个序：

1. 靠架构或更好的数据结构，让这类错误根本写不出来。
2. 靠类型系统拦死，或者加一条 lint / CI 检查，并在报错信息里直接写明正确改法。
3. 靠测试把它抓出来。
4. 写成文档或代理规则文件。代理跳过规则时什么都不会报错，所以这一层排在最后。

注意「靠人做 Code Review」压根不在列表里。要是评审人每个 PR 都得手动揪出同一个毛病，这本身就是需要解决的问题。[`/correct`](../../skills/correct/SKILL.md) 就是专门干这个的：

```text
/correct 代理老是直接调数据库客户端，不走 repository 层
```

它会去翻近期的 commit、回滚记录、评审评论以及解释绕路补丁的注释，把错误按类别归拢（同类错误出现两次就算一类）。然后按能生效的最高层级，一类一个 commit 把最高频的几类修掉，并证明每条新增检查确实能在真实的历史坏代码上报错。它还会在代理指令文件里维护一张表，把每条规矩和背后的强制检查手段一一配对，好让光靠嘴说、没人兜底的规则一眼现形。最后回复会列出每个错误类别的证据、选了哪一层根治，以及为什么更高一层用不上。

不带参数直接跑 `/correct`，它会自己从历史记录里挖出高频错误类。`/reflect` 和 `/correct` 分工很清楚：`/reflect` 从单次会话里打磨 `skill`，`/correct` 改造代码仓库让整类错误彻底绝迹。如果根治手段需要划出新的模块边界，顺手搭配 `/architect`。在 [睡觉时让它接着干](./07-overnight.md) 里有一条把两者结合起来扫描全仓的现成 `prompt`。

## 写一个聚焦的专项 `skill`

如果你心里已经非常清楚要把哪套流程固化下来：

```text
/poteto-mode 为这个仓库写一个专门验证数据库 migration 的 skill
```

写 `skill` 会命中 [Authoring or modifying a skill playbook](../../skills/poteto-mode/playbooks/authoring-a-skill.md)，自动走 Cursor 内置的 `create-skill`、校验 frontmatter 和内部链接，最后按 `Opening a PR` 提交。写给代理看的文案门槛比给人看的文档更高，因为一句废话或含糊的话，都会变成未来某个代理死板照搬的指令。让这套 `playbook` 来帮你把关，不要徒手瞎写 `SKILL.md`。

有两类特殊 `skill` 有专用生成器：需要实操驱动应用验证行为的，直接用 [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md) 和 [`/maintain-verification-skill`](../../skills/maintain-verification-skill/SKILL.md)；需要用模型检测器、定理证明或其他验证器查代码属性的，用 [`/create-formal-verification-skill`](../../skills/create-formal-verification-skill/SKILL.md) 和 [`/maintain-formal-verification-skill`](../../skills/maintain-formal-verification-skill/SKILL.md)。两类都在 [实跑验证与合入 PR](./06-verify-and-ship.md) 里详细讲过。

## 用 `/technical-writing` 按标准写技术文档

你平时交付的文字不止 `skill`。写文档、RFC、README、PR 描述和 commit message 时，可以跑：

```text
/technical-writing 审一下 README 的改动
```

[`/technical-writing`](../../skills/technical-writing/SKILL.md) 套用了一套四层写作标准，目标是让一个已经很累的工程师第一遍读下来就能看懂。它先定文档体裁（tutorial 教程、how-to 操作指南、reference 参考手册、explanation 原理解释），再逐句打磨：明确谁做了什么、一句只讲一个意思、不留任何能读出两种理解的歧义。既可以拿它审你或代理刚写好的稿子，也可以在派写文档任务时提前点名。

## 对 `skill` 改动做盲测 `eval`

改一次 `skill` 会影响往后的每一次会话，所以要像做正经实验一样先测一测。打算引入别人写的 `skill` 时同理，先验证它真能让代理把你的活干得更好再留下。

```text
/poteto-mode 对这次 skill 改动跑一遍 eval playbook。两套方案跑同一个任务，候选代理保持盲测。
```

如果某个 `skill` 老是漏动作、你又明确知道该怎么修，可以把修改和测试放进同一个任务里做完：

```text
/poteto-mode 更新一下 review skill，让它把漏写的 migration 标出来，然后对改动跑 eval。
```

一开始就要求跑 `eval` 能让改动保持克制诚实。光盯着某次翻车对话硬打补丁，很容易把 `skill` 改得过拟合；改来改去越漂越远，靠 `eval` 能在合入前就把漂移拦下来。

[Eval playbook](../../skills/poteto-mode/playbooks/eval.md) 专门防一种失效模式：观察者效应。一旦代理察觉自己正在被测评，它的表现就会失真。所以每个候选代理都在清洗过的目录里接一个看起来跟日常无异的任务，绝不出现「eval」或「candidate」这类字眼，彼此也不知道对方存在。最后由一名裁判对着匿名标签给所有产出打分；检验是否按链条读完相关 `skill` 时，只看代理实际打开过哪些文件，不信它嘴上自称读了什么。

接受裁判结论之前，自己把每份产出都看一遍。如果你跟裁判意见不一致，先怀疑评分标准没写准，别先怀疑你自己的判断。

## 用 `/make-bot-ui` 搭一个机器人面板

这里还有一个面向 Grok Bot 用户的场景 `skill`。[`/make-bot-ui`](../../skills/make-bot-ui/SKILL.md) 帮你搭一个轻量网页，上面的按钮可以通过 webhook routine 唤醒机器人，比如快速滑过一条待审队列，每划一项就让机器人执行对应操作。webhook 的 sender key 保存在你本机服务端里，绝不暴露给浏览器或聊天框。里面也顺带讲了怎么通过 Tailscale 把页面暴露出来。

**避坑提醒：** 干活中途发现 `skill` 抽风，别顺手在当前业务分支里改它。另开一个独立 PR 修 `skill`，手头任务照常推进。把 `skill` 改动夹杂在业务功能 PR 里，既不好审，也没法单独做评估。

下一篇：[实用套路与常见深坑](./10-recipes-and-pitfalls.md)。
