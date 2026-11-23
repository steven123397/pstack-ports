### Trace forensics

**基于既得产物的诊断归你把关。**

与给活进程打点的 **Runtime forensics** 不同，这里的抓取文件已经现成摆在手里。产物是一份固定数据集，直接读它分析，别想着重跑一遍。工具尽量保持通用：cpuprofile 和 `.json.gz` 用 DevTools 或 trace 解析器，spindump 用文本工具，heapsnapshot 用常规堆分析工具。

1. 识别产物格式并用趁手的工具加载。大体积产物交给子代理去解析（遵循 **principle-guard-the-context-window** `skill`），主线程只留浓缩结论。按 `Subagents` 一节选好子代理推理档位和速度。
2. 把原始产物转成可查询的形态。把 trace 或 heap snapshot 导进 sqlite，每个采样点、调用帧或节点占一行。先变好查，再开始读。
3. 一步步逼近根因。查出耗时最重的热点帧，顺着调用树走出热路径；查内存泄漏就沿着 retainer 引用链从泄漏对象追回 GC root；看 spindump 就揪出死占 CPU 或被阻塞的线程以及它的等待原因。
4. 归因到源码。用产物自带的符号表把热点帧映射到具体文件、符号和行号。一个没落到源码映射的调用帧还不算诊断结论。把符号解出来，或者老实直说产物里压根没带符号信息。
5. 如果手头有前后成对的抓取文件，把优化前后做 diff 相互印证；没有的话，把结论明确标为「当前产物支持的最强假设」，别冒充已确诊根因。
6. 交回一份带出处的诊断，除非要求否则不改代码。查明原因后再转去 `Bug fix` 或 `Perf issue`。`throughput checkpoint` 保持一行：`throughput checkpoint: n/a, read-only forensics`。

**Reply：** 产物及格式、浓缩后的核心发现、源码定位、产物路径，以及是否有成对抓取文件印证。
