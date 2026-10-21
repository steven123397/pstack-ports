# pstack 中文自读版

poteto 的 pstack（Cursor 插件，v0.15.29）的中文翻译，**给自己读、便于理解每个 skill 在做什么**，不是可安装插件。执行时请安装官方 pstack。

- 底稿：[fenfenxu/pstack-zh](https://github.com/fenfenxu/pstack-zh) 的译文（基准 0.15.28，提交 `d457567`），已对齐到 0.15.29。
- 英文原文：`../../upstreams/pstack/pstack/`（cursor/plugins 的 pstack 目录，v0.15.29）。
- 上游版权归 Lauren Tan（MIT）。fenfenxu 译文版权归 learn-pstack contributors。

## 相对 fenfenxu 底稿的改动

1. **对齐 0.15.29**：上游重做了 `sharpen` skill（旧版「磨完任务后接着干活」→ 新版「只重写 prompt、不做任务」），已更新 6 处：`skills/sharpen/SKILL.md`、`skills/poteto-help/SKILL.md`、`skills/poteto-help/references/recipes.md`、`guide/02-poteto-mode.md`、`guide/10-recipes-and-pitfalls.md`、`guide/plugin-readme.md`。
2. **补译**：`docs/harness/claude-code.md`（Claude Code 适配层）和 `automations/benny/` 的两份入口文件（`README.md`、`FOR_AGENTS.md`）。
3. **未译（自读版不需要）**：benny 的 `skills/`、`templates/` 深层文件（自动化源码，约 1500 行，Cursor 专属）；poteto-mode 的 `scripts/`（TS 代码）。需要时读 `../../upstreams/pstack/pstack/` 里的英文原文。
4. **保留**：fenfenxu 的 `tutorials/`（原创中文教程）、`glossary.md`（术语表：playbook/skill/lane/swarm 等保留英文不译）。

## 目录

| 目录 | 内容 |
|---|---|
| `skills/` | 56 个 skill 译文。入口：[`skills/INDEX.md`](skills/INDEX.md)（注意其统计行写 49/22，实际 56 skill / 24 原则）。核心是 `poteto-mode/`：主 skill + 23 个 playbook + references |
| `agents/` | 2 个子代理译文：poteto-agent、comment-sicko |
| `guide/` | 官方 10 章指南 + 插件 README 译文。从 `guide/index.md` 读起 |
| `tutorials/` | fenfenxu 写的「认识 pstack」中文教程 |
| `glossary.md` | 术语表，改译法先改它 |
| `docs/harness/claude-code.md` | Claude Code 适配层译文 |
| `automations/benny/` | benny 自动化包：入口两份已译，深层文件保留英文 |

## 阅读顺序建议

1. `guide/index.md` → `guide/01-setup.md` → `guide/02-poteto-mode.md`（官方指南前三章）
2. `skills/poteto-mode/SKILL.md`（整个体系的中枢，149 行）
3. `skills/INDEX.md` 查表，按需读单个 skill
4. 想系统理解 24 条原则：`guide/08-principles.md` + `skills/principle-*/SKILL.md`

## 与上游同步

本地是完整 git 克隆。上游更新后：

```bash
git fetch origin
git diff HEAD origin/main -- pstack   # 看增量
```

把改动文件按 `glossary.md` 的规则补译进本目录即可。fenfenxu 仓库本身也在持续跟进（有自动化翻译流水线），重大版本跳跃时可以重新拉它的底稿再打增量。
