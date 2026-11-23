---
name: principle-attack-the-premise
description: "基于同一个前提的两次或以上修复都在同一道关口失败时适用。先把这个前提写下来直接验证，再决定要不要写下一个基于它的修复。"
disable-model-invocation: true
---

# Attack the Premise

当基于同一个前提的两次或以上修复，都在同一道关口失败时，该怀疑的是那个前提本身，而不是修复手法。

**为什么这么做。** 每一次失败的修复，都是反驳它所依赖假设的证据。继续在同一个前提上试第三次，只会把力气花在证据已经排除了的方向上。

**做法：**
- **把前提明明白白写下来。** 这个前提，就是前面每次失败修复共同默认的那一句话。
- **写下一个修复前，先验证前提。** 找一个在前提为假时会给出不同结果的观测手段，实际测出来。不仅要看失败的幅度有多大，还要看失败是怎么分布的。按 [Build the Lever](../principle-build-the-lever/SKILL.md)，把这个检查做成可重复运行的脚本。
- **顺着证据走。** 如果证据推翻了前提，根因就在别处，去查这些失败有什么前提没预测到的共同点。如果证据证实了前提，按 [Fix Root Causes](../principle-fix-root-causes/SKILL.md) 继续追问下一个「为什么」，前面的修复可能只处理了表象结果，还没碰到根因。
- **按 [Laziness Protocol](../principle-laziness-protocol/SKILL.md)，直接消除诱因，别事后找补。** 如果证据表明某一部分总是落在吃亏的一侧，就去改掉把它推到那里的机制。靠事后兜底清理的方案，既留下了病根，又给每次运行增加了额外开销。

**停手红线。** 没把前提写清楚并实测完之前，不准动手写下一个修复。

这条 `principle` 和 [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md) 不同。后者是围绕新需求重塑设计，这条则是质疑当前设计默认当真的某个事实。
