### Authoring or modifying a skill

**这份 `skill` 的行文口吻和精准度归你把关。**

1. 调用 **create-skill** `skill`（Cursor 内置，专门用于编写 `SKILL.md`）。
2. 校验这份 `skill`：确认 frontmatter 包含 `name` 和 `description`，引用的文件全部存在，跨 `skill` 链接均可解析。
3. 涉及结构化规则时补测试用例；纯主观风格类可跳过。
4. 收尾执行 **Opening a PR**。

拿不准留不留的一律删掉。只保留真正能改变代理决策的文字。直接交代要做什么，省掉多余说教；只有不解释就会看懵的规则才补理由。语气贴合适用范围。优先指向结构化的权威来源（类型、README、配置文件，遵循 **encode-lessons-in-structure** `principle`）。用到其他 `skill` 时直接指路过去，别重复抄一遍。如果反复碰到一套还没收编的常用工作流，提议新建一个 `skill`。

**Reply：** 这份 `skill` 的摘要、关键设计决策以及校验情况。
