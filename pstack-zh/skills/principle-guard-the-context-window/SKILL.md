---
name: principle-guard-the-context-window
description: "上下文快塞满时适用，比如长输出、大文件、反复读文件、扇出规划。把大块头的活全派给子代理，主对话只留摘要，不塞原始大段输出。"
disable-model-invocation: true
---

# Guard the Context Window

**为什么这么做。** 上下文溢出会拉低推理质量、带来压缩失真，甚至让推进彻底卡死。

**做法：**
- **控好阶段体量，给范围封顶。** 限制每个阶段改动的文件数，定好轮次预算，把机制本身的开销也算进账里。
