# pstack-ports

基于 [cursor/plugins 的 pstack](https://github.com/cursor/plugins/tree/main/pstack)（当前锁定 `0.15.42` @ `bf0c7cd`，MIT）重建的**高质量中文精译与 `omp`（oh my pi）中文版适配仓库**。

## 为什么推翻重来

旧版直接从英文原文改写成英文版 `pstack-omp`，且尝试覆盖多个能力参差不齐的 harness（Kimi Code、DSH 等），导致两个核心问题：

1. 缺乏一版专业、地道、去翻译腔与 AI 腔的中文方法论底座，很难直接通读吃透原版，也难以判断适配版究竟改了什么。
2. 多平台静态副本维护成本高，而部分 harness 并不具备支撑 pstack 多代理隔离与验证闭环的能力。

本次重构聚焦一条主线：

1. **阶段一 · 中文原版底座（`pstack-zh/`）**：先依据英文原文逐字核校术语与语境，做出地道、克制、无翻译腔的中文版 `pstack`（含完整 `docs/guide/` 与全部 `skills/`）。
2. **阶段二 · `omp` 中文适配版（`pstack-omp/`）**：以 `pstack-zh/` 为根基派生中文版 `omp` 插件，使所有 skill、playbook 与适配改动都可用中文直接审计 diff。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| [`UPSTREAM.json`](UPSTREAM.json) | 上游基线版本锁（`0.15.42` @ `bf0c7cd`）与参考源定义 |
| [`GLOSSARY.md`](GLOSSARY.md) | 统一术语表、一词多义分译表与中文行文规范 |
| [`.upstream/`](tools/upstream/sync.mjs) | 只读上游快照（gitignored），由 `node tools/upstream/sync.mjs` 拉取 |
| [`docs/omp-platform-notes.md`](docs/omp-platform-notes.md) | 从 v1 归档打捞的 `omp` 实测平台事实与避坑备忘 |
| [`tools/`](tools/) | 上游同步脚本与引用/结构校验脚本 |
| `pstack-zh/` | 阶段一产物：忠于原版的中文版 `pstack`（待建） |
| `pstack-omp/` | 阶段二产物：基于 `pstack-zh/` 的中文版 `omp` 插件（待建） |

> 之前的 v1 尝试（原英文 `pstack-omp`、`pstack-kimi`、`pstack-dsh`、`pstack-claude` 研读笔记）已完整封存在本地归档分支 `archive/v1-attempts`。

## 常用命令

```bash
node tools/upstream/sync.mjs          # 按 UPSTREAM.json 拉取 .upstream/ 对照源
node tools/upstream/sync.mjs --check  # 检查上游在 pin 之后是否有新提交
```

## 许可

上游 `pstack` 归 Lauren Tan（poteto），采用 MIT 许可；本仓库的译文与适配层沿用 MIT 许可。
