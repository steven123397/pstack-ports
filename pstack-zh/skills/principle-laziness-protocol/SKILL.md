---
name: principle-laziness-protocol
description: "重构、评估 diff 大小，或者动念头想加抽象层、加封装或层层透传信号时适用。优先删代码，只做能解决问题的最小改动。"
disable-model-invocation: true
---

# Laziness Protocol

- **把判断收口到一处。** 不要在好几个地方重复做同样的判断。把它收进唯一的单一事实源，把结果作为一个简单标志往下传。
- **尽量压小 diff。** 做能解决问题的最小改动。少写几行代码，强过「看似优雅」的样板代码。
