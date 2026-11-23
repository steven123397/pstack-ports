# pstack 使用指南

用好 `pstack` 的前提，是别再事无巨细地管着代理。你只需要说清楚想要什么，以及怎么判断算做完。`/poteto-mode` 会自己挑出合适的 `playbook`，按步骤拉起其他 `skill`，最后把实跑证据交给你。这份指南用真实的 `prompt` 示例，带你养成这套用法习惯。

整份指南共十篇：

1. [安装与配置](./01-setup.md)。装好插件，挑好模型。
2. [用 `/poteto-mode` 统领任务](./02-poteto-mode.md)。给它一个目标，看它怎么匹配 `playbook`。
3. [动手前先读懂代码](./03-understand.md)。先做只读调研，在改代码前用好 `/how`、`/why`、`/teach` 和 `/recall`。
4. [写代码前先敲定设计](./04-design.md)。在代码把形状锁死之前，用 `/architect`、`/arena`、`/swarm`、`/interrogate`、原型和计划定好方案。
5. [开发实现与清理 diff](./05-build-and-clean.md)。几套开发 `playbook`，加上 `/tdd`、`/unslop` 和 `/no-comments`。
6. [实跑验证与合入 PR](./06-verify-and-ship.md)。在真实应用上证明行为正确，用形式化验证兜住测试测不到的角落，用 `/benchmark-checklist` 核查性能数字，再开出聚焦的 PR 并推进合入。
7. [睡觉时让它接着干](./07-overnight.md)。开循环前先建立信任，签好无人值守交接约定，留一份可审计决策日志，再用 Projects 和自动化把规模放大到多代理。
8. [用 `principle` 名称中途纠偏](./08-principles.md)。记住这 24 个名字，一句话把跑偏的代理拉回来。
9. [改成你自己的工作流](./09-make-it-yours.md)。生成个人模式，用 `/correct` 根治反复犯的错，以及如何盲测 `skill` 改动。
10. [实用套路与常见深坑](./10-recipes-and-pitfalls.md)。直接能抄的 `prompt` 模板，和别人已经替你踩过的坑。

第一次读建议按顺序过一遍，之后每一篇都可以单独拿来查。

中途卡住，或者拿不准当前场景该用哪个 `skill`，直接带着问题敲 [`/poteto-help`](../../skills/poteto-help/SKILL.md)：

```text
/poteto-help 审这个分支我该用哪个 skill？
```

它会先答复你，给你一条现成能发的 `prompt`，并附上答案出处对应的 `skill` 或指南链接。它不会直接替你开工，因为跑一轮 `pstack` 要花不少 token，由你确认后再把那条 `prompt` 发出去。只有你主动敲 `/poteto-help` 时它才会运行。

## 如果你只记住一件事

用你自己的大白话，给代理一个目标和一个可检验的完成标准：

```text
/poteto-mode 任务跑一半遇到重试时，导出功能会写出重复行。先复现，再修复并验证。
```

你完全不需要指定 `playbook` 名字，也不要手列一串 `skill`。「先复现」加上可检验的完成结果，就已经给了 `/poteto-mode` 足够的路由信号。它会自动匹配 `Bug fix` playbook，把步骤抄进待办清单，跑每一步时自己调起需要的 `skill`。

下一篇：[安装与配置](./01-setup.md)。
