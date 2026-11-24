# pstack-ports

基于 [cursor/plugins 的 pstack](https://github.com/cursor/plugins/tree/main/pstack)（当前同步至 `0.15.48` @ `9e278fe`，MIT）维护的中文精译与平台迁移参考仓库。

## 翻译说明

本仓库目前已完成 [`pstack-zh/`](pstack-zh/) 的全量中文精译（含完整 `docs/guide/` 指南、全部 `skills/`、`playbooks/` 与 `agents/`）。

翻译时遵循 [GLOSSARY.md](GLOSSARY.md) 的统一术语与行文约定，目标是在忠实保留作者原意与技术准确性的前提下，尽量贴合中文开发者的阅读与表达习惯，去掉生硬直译和常见的 AI 腔，希望提供一版可以直接通读、便于吸收的中文参考读本。

## 使用建议

[`pstack-zh/`](pstack-zh/) 的结构和路径与上游原版保持一致，技术上可以直接装进支持 Agent Skills 的 harness 中运行，但**并不建议不加改动地直接照搬使用**：

1. **与 Cursor 生态高度耦合。** 原版 `pstack` 大量依赖 Cursor 的专属设施（如子代理模型路由、`Custom Mode`、云端代理、`/loop`、`cursor-team-kit` 与 Automations 等），直接套用到其他 agent harness 往往难以发挥原设计的效果，甚至出现流程断裂。
2. **高度契合作者本人的角色与习惯。** 这套工作流是 Lauren Tan（poteto）站在企业级项目与首席工程师（Principal Engineer）视角下总结出来的，与它最严丝合缝的始终是她本人的工作节奏与工程标准。每位开发者面对的项目规模、团队规范与个人偏好都不尽相同，更推荐先深度通读、吃透背后的工程思路，再按自己的习惯删减组件、改写细则，长出适合自己的工作流。

## 关于 `v0.15.42` 学习快照

上游从 `0.15.43` 起对 14 条 `principle`、`architect`、`reflect` 及多篇核心 `playbook` 做了大幅正文瘦身，将大量「为什么」与举例压缩为面向新一代强模型的精炼规则。

如果你希望系统学习 `pstack` 背后的方法论推导与完整展开范本，推荐一并查阅已封存的 **[`pstack-zh-v0.15.42` Release](https://github.com/steven123397/pstack-ports/releases/tag/pstack-zh-v0.15.42)**。该版本完整保留了瘦身前的详尽原理阐述、反模式示例以及多代理参考模板，依然具有很高的学习与参考价值。

## 后续计划

- **持续跟进上游。** 本仓库会持续追踪上游 `pstack` 的演进并同步更新中文精译。
- **`omp`（oh my pi）迁移示例。** 后续会以 `pstack-zh/` 为底座，在本仓库中补充一份面向 `omp` 的中文迁移适配示例（`pstack-omp/`）。
- **个人化适配案例。** 之后也会在独立仓库里，结合我自己的日常开发习惯对 `pstack` 做针对性裁剪与调整，作为一份真实落地的个性化改造案例供大家参考。

欢迎提 Issue 或 PR，无论是译文润色、术语探讨、勘误纠偏，还是围绕 `pstack` 方法论与跨平台适配的交流都非常欢迎。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| [`pstack-zh/`](pstack-zh/) | 忠于上游原版的中文精译版 `pstack`（当前版本 `0.15.48`） |
| [`UPSTREAM.json`](UPSTREAM.json) | 上游基线版本锁（`0.15.48` @ `9e278fe`）与只读参考源定义 |
| [`GLOSSARY.md`](GLOSSARY.md) | 统一术语表、一词多义分译表与中文行文规范 |
| [`docs/omp-platform-notes.md`](docs/omp-platform-notes.md) | `omp` 实测平台事实与适配避坑备忘 |
| [`tools/`](tools/) | 上游同步脚本与引用/结构保真校验脚本 |
| `pstack-omp/` | 后续计划：基于 `pstack-zh/` 的 `omp` 中文迁移示例 |

## 许可

上游 `pstack` 归 Lauren Tan（poteto），采用 MIT 许可；本仓库的中文译文与适配层沿用 MIT 许可。
