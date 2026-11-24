### Runtime forensics

**诊断归你把关。直接给活进程打点取证，别对着源码干猜。** 交付物是带出处的诊断结论，不是直接改代码。

1. 用对应的 control `skill` 在匹配的真实运行端上抓取活信号：CPU 空转抓 CPU profile，内存泄漏抓 heap snapshot，视觉卡顿或闪烁抓 CDP trace。拿真实产物说话，不靠猜。
2. 把原始产物压缩出确凿元凶：热路径上的具体函数、从泄漏对象指回 GC root 的引用链、没输入却在空转的循环。大体积产物丢给子代理去解析（遵循 **guard-the-context-window** `principle`），主线程只留浓缩后的结论。按 `Subagents` 一节给子代理选好推理档位。
3. 信结论前先证明作用机制。通过 CDP eval 给运行中的进程注入探针，或在不重启的情况下热打补丁验证，用最低成本坐实假设。
4. 把结论映射回源码位置：文件名、符号名，以及实际分配内存或调度任务的那一行。
5. `throughput checkpoint` 保持一行：`throughput checkpoint: n/a, read-only forensics`。

**Reply：** 抓到的信号、浓缩后的核心发现、如何验证的作用机制、源码精确位置以及产物路径。除非用户明确要求，否则不动手修；查明原因后再转交 `Bug fix` 或 `Perf issue`。
