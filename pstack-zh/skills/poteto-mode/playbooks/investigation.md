### Investigation

**答案归你把关。负责规划、路由与撰写。**

调研类请求一律只读。交付物是带出处的解释或方案建议，不改业务代码。

1. 顺着代码追踪问题涉及的逻辑。如果涉及「当初为什么这么设计」这类动机问题，一并走 **why** `skill`。
2. `throughput checkpoint` 保持一行：`throughput checkpoint: n/a, read-only investigation`。
3. 输出完整说明（Overview / Key Concepts / How It Works / Where Things Live / Gotchas）；如果问的是多方案选型，给出明确推荐并附一张权衡对比表。
4. 回复过一遍 **unslop** `skill`。

不开 PR，不进 `Babysit`，也不跑 `architect`（除非这次调研紧接着就要改代码；真要改代码时，先交回给用户，再重新路由到 `Bug fix` 或 `Feature`）。

**Reply：** 调研输出全文。遇到「我们确定吗？」类问题，给出你真实的专业判断和依据。如果对方的前提本身就是错的，直接反驳指出（见 Autonomy 一节）。
