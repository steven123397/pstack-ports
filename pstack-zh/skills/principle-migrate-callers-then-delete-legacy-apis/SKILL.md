---
name: principle-migrate-callers-then-delete-legacy-apis
description: "引入新内部 API 而旧调用方仍在时适用。在同一轮改动里迁完所有调用方并立即删掉旧接口，别保留兼容过渡层。"
disable-model-invocation: true
---

# Migrate Callers Then Delete Legacy APIs

- 同步更新测试去断言新契约，把只用来保护重构前实现细节的旧测试直接删掉

**适用前提：**
- 没有外部用户依赖向后兼容
- 项目能承受协调一致的破坏性变更
- 新 API 本身就属于一次简化或重构行动
