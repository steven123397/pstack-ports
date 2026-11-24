---
name: principle-type-system-discipline
description: "设计类型、审查函数签名或在任何静态类型语言里写代码时适用。让非法状态在类型上无法构造，用 Branded Types 区分语义不同的基础类型，在边界解析外部数据，穷尽所有分支变体，并从权威 schema 派生类型。"
disable-model-invocation: true
---

# Type System Discipline

让编译器直接拒掉不可能的状态、张冠李戴的基础类型和漏掉的分支变体。

- **用 Branded Types 区分语义不同的基础类型。** 只要两个参数底层共享同一基础类型但业务含义不同，就各自建独立类型，在构造时校验一次。
- **外部数据未经解析前一律视为无类型。** JSON、RPC 载荷、CLI 参数、配置、环境变量和数据库行，统一在系统边界经过解析函数转成强类型模型。
- **从权威 schema 派生类型。** 只要已有 schema 文件定义数据形状，直接从中派生类型，绝不手写一份平行副本。

关于 TypeScript 具体写法，参见 **typescript-best-practices** `skill`。
