---
name: principle-redesign-from-first-principles
description: "把新需求融入已有设计时适用。"
disable-model-invocation: true
---

# Redesign From First Principles

融入一个变更时，别直接往旧设计上硬打补丁。当作这个需求从第一天起就是基础假设，重新理顺设计。

- 通读所有受影响的文件，彻底搞懂当前设计
- 问自己：「如果今天从零开始写，且一开始就有这个新需求，我们会怎么设计？」
- 把这次变动贯穿到每一处关联位置，包括类型、文档、示例和设计缘由说明
- 先把整体重构方案想透，再分步交付落地

这是把变更融入已有设计时，保住架构演进余地的方法。
