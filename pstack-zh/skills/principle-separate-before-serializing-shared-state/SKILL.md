---
name: principle-separate-before-serializing-shared-state
description: "多个并发执行体可能同时写同一个文件、分支、键或状态对象时适用。先拆开消除共享；只有单一共享写入目标是真正的不变量时，再从结构上做串行化。"
disable-model-invocation: true
---

# Separate Before Serializing Shared State

当多个并发执行体可能同时写同一个文件、分支、键或对象时，先问清楚它们究竟是真的需要共用同一个对象，还是各自在发布彼此独立的事实。默认做法是给每个执行体分配独立的文件、键、分支或状态目录，只在读取汇总时合并。两个工人往同一个 `state.json` 里各写自己的字段，依然属于共享写入冲突。

只有当「单一共享写入目标」本身是真正的不变量时，才从结构上做串行化控制（锁文件、单一写入者、分阶段串行、compare-and-swap）。口头叮嘱不算并发控制，一旦冒出「我们得加把锁」的念头，先把它当坏味道复核一遍。
