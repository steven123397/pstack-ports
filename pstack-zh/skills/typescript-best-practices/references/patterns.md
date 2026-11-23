# TypeScript patterns

对应 `SKILL.md` 中每条规则的代码示例。背后的原则与语言无关，详见 **type-system-discipline** 和 **boundary-discipline** `principle` `skill`。

## Branded types

用 Branded Types 区分语义不同的基础类型，防止互相串传。在边界校验一次，下游代码直接信任类型。

```ts
type AgentId = string & { readonly __brand: "AgentId" };

function isAgentId(input: string): input is AgentId {
  return isUUID(input);
}

function parseAgentId(input: string): AgentId {
  if (!isAgentId(input)) throw new Error(`Invalid agent id: ${input}`);
  return input;
}

function focusAgent(id: AgentId): void {
  /* 输入已可信 */
}
```

统一采用 `readonly __brand: 'X'` 写法，不要另造新约定。

## 可辨识联合（Discriminated unions）

用字面量判别字段为各个状态变体建模。每个变体共用同一个字段名且字面量取值唯一，让不可能的状态组合在类型上根本写不出来。

```ts
// 反例。布尔值加一堆可选字段允许互相矛盾的状态同时存在。
type DiffState = { loading: boolean; diff?: GitDiff; error?: string };

// 正例。只有合法状态才能被构造。
type DiffState =
  | { kind: "loading" }
  | { kind: "ready"; diff: GitDiff }
  | { kind: "error"; error: string };
```

选定一个判别字段名（`kind`、`type` 或 `tag`）并全库保持一致。

## 构造式建模（Constructive modeling）

用本身全合法的部件拼出类型，而不是拿宽松类型配一堆运行时检查去堵漏洞。

用可变元组表达非空数组：

```ts
type NonEmpty<T> = [T, ...T[]];

// 反例：用 T[]，逼得每个调用方反复写长度检查
function pickWinner(entries: string[]): string {
  if (entries.length === 0) throw new Error("no entries");
  return entries[Math.floor(Math.random() * entries.length)];
}

// 正例：这个类型根本造不出空值
function pickWinner(entries: NonEmpty<string>): string {
  return entries[Math.floor(Math.random() * entries.length)];
}
```

入口拿到普通 `T[]` 时，用守卫收窄一次，此后这个非空事实就跟着类型一路往下传：

```ts
const isNonEmpty = <T>(arr: T[]): arr is NonEmpty<T> => arr.length > 0;
```

用二元组数组表达偶数长度：

```ts
type Pairs<T> = [T, T][];
```

用起点加时长表达时间区间：

```ts
// 反例：靠注释维持不变量
type TimeRange = { start: Date; end: Date }; // start <= end

// 正例：写不出负区间，需要结束时间时派生算出来
type TimeRange = { start: Date; durationMs: number };
```

`durationMs` 保持普通 `number` 即可。只有在裸数字真有可能被误传到需要时长的位置时，才按 Branded types 规则加 brand，别条件反射到处乱加。先选出让非法状态构造不出来的表示法，再在它之上按需提供读取辅助（如 `pairs.flat()`、`rangeEnd()`）。

## 最简全函数类型（Simplest total type）

不要把所有类型都过度收紧。只要每个操作在 `T[]` 上都有完整定义，就保持 `T[]`：

```ts
const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0); // 空数组返回 0，完全安全
```

只有在宽松类型逼着使用点对编译器撒谎时才收紧。典型破绽包括 `!`、`arr[0] as T` 以及「绝不会发生」的 throw：

```ts
// 反例：把偏函数偷偷糊弄过编译器
function newestSession(sessions: Session[]): Session {
  return sessions.at(0)!;
}

// 正例：收紧输入类型，非空断言自然消失
function newestSession(sessions: NonEmpty<Session>): Session {
  return sessions[0];
}
```

把返回值放宽成 `Session | undefined` 则是另一种全函数签名写法。

## 用 `unknown` 不用 `any`

外部数据一律先按 `unknown` 接进来，收窄之后再用。

```ts
// 反例
function handle(input: any) {
  return input.foo.bar;
}

// 正例
function handle(input: unknown) {
  if (typeof input === "object" && input !== null && "foo" in input) {
    // 已收窄，编译器校验属性访问
  }
}
```

外部数据源包括 RPC 载荷、`JSON.parse`、`postMessage`、IPC、文件内容、环境变量和数据库查询结果。

## 优先用 schema，别急着手写守卫

准备给外部数据手写逐属性类型守卫之前，先查仓库里现有的运行时 schema 库和已有 schema。让唯一一份 schema 同时掌管校验，并直接从中派生 TypeScript 类型。绝不要同时维护一份 schema、一份平行 interface 和一份手写守卫，三者早晚漂移脱节。

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(["admin", "member"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(input: unknown): User {
  return UserSchema.parse(input);
}
```

当解析失败属于正常业务分支时改用 `safeParse`。如果仓库用的是其他 schema 库，使用它对应的类型推断工具。不要为了单个守卫去引入新的 schema 依赖，这条规则优先复用代码库已经信任的那套 schema 体系。

## 禁用 `as` 强转

每一个 `as` 都是潜在的运行时崩溃。只有在类型系统已经验证过前提之后才允许强转。

```ts
import { z } from "zod";

// 反例
const user = data as User;

// 反例
function isUser(data: unknown): data is User {
  return typeof data === "object" && data !== null && "id" in data;
}

// 正例
const userSchema = z.object({ id: z.string(), name: z.string() });
type User = z.infer<typeof userSchema>;

function parseUser(data: unknown): User {
  return userSchema.parse(data);
}
```

如果类型先于校验器存在，把目标类型直接标在校验器上。这样一旦校验器少验了字段，编译器就会直接报错。把下面对象里的 `name` 删掉，赋值立刻编不过。

```ts
type User = { id: string; name: string };

const userSchema: z.ZodType<User> = z.object({ id: z.string(), name: z.string() });
```

从旧代码里重构拔掉 `as` 时，先查清 TypeScript 为什么推不出来：

- 缺判别字段：补一个判别字段，改成可辨识联合。
- 来源类型太宽（如 `Record<string, unknown>`）：把它收窄。
- 边界未做类型解析：用掌管该数据形状的 schema 解析，没有时再补 schema。
- 类型系统确实表达不了：用 branded type 或 `satisfies`。

## 类型收窄优先级

从最推荐到最后手段：

1. **可辨识联合 `switch` / `if`。** 编译器自动收窄。
2. **`in` 运算符。** `"key" in obj` 自动收窄到包含该键的变体。
3. **`typeof` / `instanceof`。** 用于基础类型与类实例。
4. **自定义类型守卫。** 上述手段都不够时使用。
5. **`as` 强转。** 仅在校验之后使用。

```ts
function area(s: Shape): number {
  if ("radius" in s) return Math.PI * s.radius ** 2; // 已收窄为 circle
  return s.width * s.height; // 已收窄为 rect
}
```

## 类型守卫（Type guards）

守卫必须真正验证它声称的条件。撒谎的守卫比 `as` 更糟糕。

```ts
function isCircle(s: Shape): s is Shape & { kind: "circle" } {
  return s.kind === "circle";
}
```

能直接靠判别字段收窄时，优先用判别字段收窄。

## 穷尽性检查（Exhaustiveness）

在 `default` 分支里，把判别对象赋给一个 `never` 类型的局部变量。

```ts
// 带返回值的 switch
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "rect":
      return s.width * s.height;
    default: {
      const _exhaustive: never = s;
      return _exhaustive;
    }
  }
}

// 无返回值的 switch
function handle(s: Shape): void {
  switch (s.kind) {
    case "circle":
      drawCircle(s);
      break;
    case "rect":
      drawRect(s);
      break;
    default: {
      const _exhaustive: never = s;
      void _exhaustive;
    }
  }
}
```

带返回值的 `switch` 用 `return _exhaustive`，语句型 `switch` 用 `void _exhaustive`。

## 用 `satisfies` 替代 `as`

`satisfies` 在校验约束的同时保留精确的字面量类型，不会拓宽。

```ts
// 反例。拓宽了类型，丢失了字面量信息。
const config = { theme: "dark", cols: 3 } as Config;

// 正例。既校验约束又保留字面量类型。
const config = { theme: "dark", cols: 3 } satisfies Config;
// config.theme 的类型是字面量 "dark"，而不是宽泛的 string
```

## 边界校验（Boundary validation）

数据跨入系统边界时校验一次，系统内部直接信任类型。详见 **boundary-discipline** `principle` `skill`。

- **协议线格式**（proto、JSON-RPC）：解析时开启 `ignoreUnknownFields`，防止向前兼容的新字段把旧客户端打挂。
- **持久化落盘 JSON：** 带版本号的数据块，解析外层包 `try/catch`。
- **绝不在调用链深处重复校验。**

## 从 schema 派生类型

只要 `.proto`、OpenAPI 规约、GraphQL schema 或数据库 migration 已经定义了数据形状，就直接从生成的类型派生，别手写一份平行拷贝。

```ts
// 反例。重复定义形状，schema 一改就会漂移脱节。
type CheckSummary = {
  totalCount: number;
  checks: { name: string; status: string }[];
};
function renderChecks(s: CheckSummary) {
  /* ... */
}

// 正例。直接从生成的 schema 类型派生。
import type { ChecksMessage } from "<generated module>";
function renderChecks(s: Pick<ChecksMessage, "totalCount" | "checks">) {
  /* ... */
}
```

写新 `interface` 之前，先用 `Pick`、`Omit`、`Parameters`、`ReturnType`、`Awaited`、`typeof`。

## 对象参数（Object args）

```ts
// 反例。把两个参数顺序写反了照样能编译过。
openFile(uri, {
  startLineNumber: 10,
  startColumn: 1,
  endLineNumber: 10,
  endColumn: 1,
});

// 正例。与顺序无关，参数含义一目了然。
openFile({
  uri,
  selection: {
    startLineNumber: 10,
    startColumn: 1,
    endLineNumber: 10,
    endColumn: 1,
  },
});
```

热路径跳过这条规则：每帧渲染、词法分析器、解析器，以及任何对象分配开销会拖慢性能的紧凑循环。
