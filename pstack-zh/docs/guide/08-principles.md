# 用 `principle` 名称中途纠偏

`pstack` 把 24 条工程原则做成了 24 个独立 `skill`。每次多步骤任务一开始，`/poteto-mode` 都会先读一遍它们的索引，命中哪条就按哪条执行，并在回复里点名用了哪些 `principle` 以及具体改变了哪个决定。

你平时不需要手动调用某条 `principle`，而是用它们的名字在中途给代理纠偏。每个名字背后都连着代理已经读过的完整细则，点出一个词，往往比你临时敲一大段指令更精准。

## 实战里怎么点名纠偏

假如代理正打算在三个老适配器外面再硬挂第四个：

```text
用 Subtract Before You Add。先把废弃的适配器删干净，再基于剩下的东西设计。
```

假如代理光凭编译通过就宣布完工了：

```text
按 Prove It Works 来。把真实导入流程跑一遍，给我看落库后的实际记录。
```

假如两个并行尝试眼看要往同一个分支里写代码：

```text
按 Separate Before Serializing Shared State 处理。每个尝试单开一个 worktree，别靠加锁硬凑。
```

这些短话之所以一叫就灵，是因为每个名字后面对应着非常具体的操作铁律。而且代理必须在回复里写明这条原则到底改变了哪个决定；如果只把原则名挂在嘴边、后面没对应具体改动，就说明它光背口号没真执行。

## 24 条 `principle` 速览

**Core（核心原则）** 决定该写多少代码，以及什么时候该推倒重想：

- [Laziness Protocol](../../skills/principle-laziness-protocol/SKILL.md)：优先删代码，选择能解决问题的最小改动。
- [Foundational Thinking](../../skills/principle-foundational-thinking/SKILL.md)：写业务逻辑之前先把核心数据结构定好。
- [Redesign from First Principles](../../skills/principle-redesign-from-first-principles/SKILL.md)：融入新需求时，按「从第一天起就有这个需求」的思路重新设计。
- [Attack the Premise](../../skills/principle-attack-the-premise/SKILL.md)：共享同一个前提的两次及以上修法都失败时，把那个前提写出来直接检验，别再默认它成立。
- [Subtract Before You Add](../../skills/principle-subtract-before-you-add/SKILL.md)：在往上叠新代码之前，先把死代码和冗余包袱减掉。
- [Minimize Reader Load](../../skills/principle-minimize-reader-load/SKILL.md)：拍平多余的跳转层级，减少读代码的人要在脑子里硬记的隐式状态。
- [Outcome-Oriented Execution](../../skills/principle-outcome-oriented-execution/SKILL.md)：做重写和迁移时直接朝目标架构收敛，别保留注定要扔的过渡兼容代码。
- [Experience First](../../skills/principle-experience-first/SKILL.md)：把用户的真实体验排在实现图省事前面。
- [Exhaust the Design Space](../../skills/principle-exhaust-the-design-space/SKILL.md)：遇到没有先例的设计分叉，先做两三个互相竞争的原型对比再定。
- [Build the Lever](../../skills/principle-build-the-lever/SKILL.md)：动手造出能干活或能证明结果的脚本，方便评审人复跑。如果代理反复手工干同一件事，就让它先写出自己趁手的工具或 `skill`。凡是脚本每次都能按同样方式跑完的步骤，都交给脚本，把代理的脑力留给真正需要判断的地方。

**Architecture（架构原则）** 决定状态、校验和兼容性该落在哪一层：

- [Model the Domain](../../skills/principle-model-the-domain/SKILL.md)：把反复出现的业务规则收拢进单一数据结构，别写一地散落的条件分支。
- [Boundary Discipline](../../skills/principle-boundary-discipline/SKILL.md)：校验防线集中在系统边界，内部充分信任类型。
- [Type System Discipline](../../skills/principle-type-system-discipline/SKILL.md)：让非法状态在类型系统里根本构造不出来。
- [Make Operations Idempotent](../../skills/principle-make-operations-idempotent/SKILL.md)：确保重复执行和崩溃重试都能收敛到同一个终态。
- [Migrate Callers Then Delete Legacy APIs](../../skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)：在同一波改动里迁完所有调用方并立即删掉旧接口。
- [Separate Before Serializing Shared State](../../skills/principle-separate-before-serializing-shared-state/SKILL.md)：先想办法拆开消除共享，别急着加锁或串行化协调。

**Verification（验证原则）** 划定什么才算真证据：

- [Prove It Works](../../skills/principle-prove-it-works/SKILL.md)：对着真实产物验证，不拿表面替代指标交差。
- [Fix Root Causes](../../skills/principle-fix-root-causes/SKILL.md)：先复现、追到根因再改代码。
- [Sequence Work into Verifiable Units](../../skills/principle-sequence-verifiable-units/SKILL.md)：拆成以检查收尾的小单元，验完一个再干下一个。
- [Test Behavior, Not Implementation](../../skills/principle-test-behavior-not-implementation/SKILL.md)：只断言外部使用方能观察到的行为，确保行为坏掉时测试必挂、只调内部实现时测试依然通过。
- [Explain the Number](../../skills/principle-explain-the-number/SKILL.md)：在任何人相信或汇报一个实测数字之前，先说清限制它的瓶颈，并排除测偏了的可能。[`/benchmark-checklist`](../../skills/benchmark-checklist/SKILL.md) 把这条原则落成了七个必须拿实跑回答的问题。

**Delegation（委派原则）** 管住并行协作不失控：

- [Guard the Context Window](../../skills/principle-guard-the-context-window/SKILL.md)：大块读代码丢给子代理，主对话只留精炼结论。
- [Never Block on the Human](../../skills/principle-never-block-on-the-human/SKILL.md)：可撤回的工作先干完把结果端出来，别卡着等人点头。

**Meta（元原则）** 只有一条：

- [Encode Lessons in Structure](../../skills/principle-encode-lessons-in-structure/SKILL.md)：同一句叮嘱如果重复说了两次，就把它写成 lint、自动检查或脚本。[`/correct`](../../skills/correct/SKILL.md) 把这条原则应用到整个代码仓库，详见 [改成你自己的工作流](./09-make-it-yours.md)。

不用死记硬背这份清单。现在先扫个眼熟，以后每次撞见代理干了一件「这表里正好有个名字能治它」的蠢事时回来翻一眼，词汇自然就记牢了。

下一篇：[改成你自己的工作流](./09-make-it-yours.md)。
