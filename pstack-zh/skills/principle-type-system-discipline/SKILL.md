---
name: principle-type-system-discipline
description: "设计类型、审查函数签名或在任何静态类型语言里写代码时适用。让非法状态在类型上无法构造，用 Branded Types 区分语义不同的基础类型，在边界解析外部数据，穷尽所有分支变体，并从权威 schema 派生类型。"
disable-model-invocation: true
---

# Type System Discipline

让编译器替你拦下不可能的状态组合、串错类型的基础值以及漏处理的分支。宁可在类型定义里把错误和特例直接设计成「根本不存在」，也不要写一堆兜底处理代码。TypeScript 具体语法写法见 `typescript-best-practices` `skill`。

- **用 Branded Types 区分语义不同的基础类型。** `UserId` 和 `OrderId` 底层虽然都是字符串，但绝不该允许互相乱传。给它们各自独立的类型，比如在 TypeScript 里用 branded intersection，在其他语言里用 newtype。在创建边界校验一次，下游全权信任类型。只要两个参数底层都是基础类型但业务语义不同，就给它们区分开。
- **外部数据在解析前都算无类型数据。** RPC 载荷、JSON、IPC 消息、CLI 参数、配置文件、环境变量、数据库行数据，统统如此。每道系统边界都要放一个 parse 函数，把非结构化输入转成强类型模型再放进内部。校验具体该放哪一层，看 **boundary-discipline** `principle`。
- **从权威 schema 派生类型。** 只要有 Protobuf、OpenAPI 规约、GraphQL schema、数据库 migration、design-token 文件或其他源头明确拥有这个数据形状，就直接从它派生类型，别手写一份平行重复的类型定义。配套看 **encode-lessons-in-structure** `principle`。
