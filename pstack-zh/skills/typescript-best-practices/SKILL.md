---
name: typescript-best-practices
description: "TypeScript 最佳实践。阅读或编辑任何 .ts 或 .tsx 文件时适用。"
paths: ["**/*.ts", "**/*.tsx"]
disable-model-invocation: true
---

# TypeScript best practices

先应用 **type-system-discipline** `principle` `skill`。

| 规则 | 要点 |
|------|---------|
| 可辨识联合（Discriminated unions） | 用字面量判别字段 `kind` 建模各状态变体，让非法状态在类型上无法构造。不要堆一堆可选字段的万能对象。 |
| Branded types | 用 `& { readonly __brand: "X" }` 区分语义不同的基础类型，防止互相串传。在边界校验一次。brand 必须来自真正执行校验的类型守卫（`input is AgentId`），绝不靠 `as` 硬贴。 |
| 构造式建模（Constructive modeling） | 把数据形状设计成根本构造不出非法值。非空数组用 `[T, ...T[]]`，偶数长度用 `[T, T][]`，时间段用 `start` 加 `duration`。别靠运行时防御，也别空等 refinement types。 |
| 最简全函数类型（Simplest total type） | 只要所有操作在 `T[]` 上都是全定义（total）的，就保留 `T[]`。只有在宽松类型逼着调用点写 `!`、强转或「绝不会发生」的 throw 时，才收紧成 `NonEmpty<T>`。 |
| 用 `unknown` 不用 `any` | 一切外部数据一律先标为 `unknown`。 |
| 优先用 schema 而不是手写守卫 | 手写逐属性类型守卫之前，先用仓库已有的运行时 schema 库，并从 schema 派生类型（例如 `z.infer`）。 |
| 禁用 `as` 强转 | 每一个 `as` 都是埋伏好的运行时崩溃。只有在校验之后才允许强转。 |
| 类型收窄优先级 | 可辨识联合 `switch` > `in` 运算符 > `typeof`/`instanceof` > 自定义类型守卫 > `as`。 |
| 类型守卫（Type guards） | 必须真验证它声称的条件。撒谎的守卫比 `as` 更毒，因为它把 bug 藏在一个看着很安全的名字后面。命名统一用 `isX` 或 `hasX`。 |
| 穷尽性检查（Exhaustiveness） | 在 `default` 分支写 `const _exhaustive: never = x;`，确保以后新增变体时编译器直接报错。 |
| 用 `satisfies` 替代 `as` | 既校验值符合约束，又不会把字面量类型拓宽。 |
| 边界校验（Boundary validation） | 数据跨入边界时立刻解析成具名领域类型。不管写成什么样，`Record<string, unknown>` 必须止步于解析边界。系统内部直接信任类型。详见 **boundary-discipline** `principle` `skill`。 |
| 从 schema 派生类型 | 声明新 interface 前，先用 `Pick`/`Omit`/`Parameters`/`ReturnType`/`Awaited`/`typeof` 派生。 |
| 对象参数（Object args） | 传对象而不是按位置传一长串参数，让参数顺序自解释。热路径（每帧渲染、词法分析器、解析器）跳过此条。 |
| 跑真实测试 | 本地能真实跑起来的东西就别 mock。优先用框架自带的真实测试原语并带上泄漏与资源释放检查，UI 改动要在真实构建运行中验证。只 mock 本地确实跑不了的外部依赖。 |
| 结构化可观测日志 | 优先用结构化 logger 输出带足够上下文的诊断信息，做到凭一个 id 就能查清问题。上线代码里禁止留 `console.log`。 |

代码示例见 `references/patterns.md`。
