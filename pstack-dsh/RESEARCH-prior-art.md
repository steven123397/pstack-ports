# DSH 移植前调研：现成方案与可自建能力

调研日期 2026-10-24。目标平台 DeepSeek Harness（本机安装器 0.2.1-rc.2，运行时 `@deepseek-ai/dsh-*` 包版本 **0.2.1-rc.3**，`@deepseek-ai/cordis` 4.0.5，node 24.21.0 / pnpm 11.28.5）。上游 pstack v0.15.29（`cursor/plugins` commit `88d4751`）。

证据分级：`[L]` 本机安装直接读出（`app.asar` 内的包 README / `~/.dsh` 配置）；`[W]` 仅网页搜索结果；`[I]` 推断。星数、提交时间为检索时刻快照，会变；结论以"结构是否匹配"为主。

## 结论先行

1. **现成方案有，而且不止一个**：GitHub 上已有 5 个 pstack → DSH 的移植，全部是个人项目，最早 2026-08-15，最新 2026-10-21。
2. **最完整的文档是 [`aa2246740/pstack-dsh`](https://github.com/aa2246740/pstack-dsh)**（6★，v0.2.3，46 skills，`HARNESS.md` 逐条引用 DSH 源码路径）。但它同步的是上游 **0.15.0**，比我们基线落后约 40 天、少 10 个 skill。
3. **最贴近我们基线的是 [`dgh52ohp125-tech/pstack-dsh`](https://github.com/dgh52ohp125-tech/pstack-dsh)**：同步到 **0.15.29**（2026-10-21），258 个文件、142–156 项测试、CI 每日检查上游发版，并把对上游正文的改动抽成 `overrides/` 数据层。代价是 0★、单作者、账号像一次性账号，可信度需要自己验。
4. **关键更正：那三个移植都是在 DSH 0.2.0-rc 上做的，而本机 0.2.1-rc.3 已经把大部分缺失能力做成原生 seam。** 它们自造的 `pstack_spawn` + overlay，在 0.2.1 上大概可以简化成配置：`subagent` 已支持 `agentOptions{provider, model, reasoningEffort, maxTokens}`、`agentPreset`、`allowedAgentPresets` 与 `list_subagent_models`；只读/受限工具面靠 agent preset 的 `toolFilter`；transcript 考古有 `dsh-experimental-session-search` / `dsh-session-query-sqlite`。**真正要自己写的只剩 per-child worktree 隔离，以及把 56 个 skill 打进可分发 bundle 的管线。**
5. **建议**：不要照抄旧移植的"造工具"路线，按 0.2.1 的原生 seam 重新设计；先做一次真机验证清单，再决定是 fork 现成件还是自建。产物形态是 **DSH plugin bundle**，不是"一堆 SKILL.md"。

## 一、pstack 移植全景（非 DSH，作为映射对照）

`pstack` 的跨 harness 生态已经很密。检索到的、描述明确是 pstack 移植的仓库（按星数）：

| 仓库 | 目标平台 | 星数 | 备注 |
| --- | --- | --- | --- |
| [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) | Claude Code、Codex、Copilot、Pi、OpenCode、Gemini、Prime | 3348 | 多 harness 一体，`tools/forks.json` 声明每处策略分叉 |
| [backnotprop/pstack](https://github.com/backnotprop/pstack) | Claude、Codex、Pi | 2668 | |
| [ericlitman/open-pstack](https://github.com/ericlitman/open-pstack) | Claude Code、Codex | 519 | 跟踪上游 |
| [chhoumann/t3-pstack](https://github.com/chhoumann/t3-pstack) | T3 Code | 226 | 面板 + 跨模型 fan-out |
| [negoro26/pstack-omp](https://github.com/negoro26/pstack-omp) | omp | 9 | 与本仓库 `pstack-omp/` 同一目标平台 |
| [Aqua-123/pstack-for-codex](https://github.com/Aqua-123/pstack-for-codex)、[ScriptedAlchemy/pstack-codex](https://github.com/ScriptedAlchemy/pstack-codex) | Codex | 95 / 71 | Codex 原生插件 + marketplace |
| [Luks3110/pstack-zcode](https://github.com/Luks3110/pstack-zcode) | ZCode | 9 | |
| [Cloeille/pstack](https://github.com/Cloeille/pstack)、[iap/pstack-hermes](https://github.com/iap/pstack-hermes) | Hermes Agent | 12 / 25 | |
| [cang-pham-codeleap/pstack-omp](https://github.com/cang-pham-codeleap/pstack-omp)、[dsebban/skills](https://github.com/dsebban/skills)、[ajoslin/eng-mode](https://github.com/ajoslin/eng-mode) | omp | 0 / 67 / 6 | |

对本次移植有用的不是代码，而是它们暴露的**难点分布**：同一个 pstack 在不同平台，被改写的部分高度集中在四处——子代理模型路由、只读/隔离、session transcript 路径、PR/云执行。

## 二、DSH 现成方案（5 个）

| 仓库 | 上游基线 | 覆盖 | 自造能力 | 质量信号 | 风险 |
| --- | --- | --- | --- | --- | --- |
| [aa2246740/pstack-dsh](https://github.com/aa2246740/pstack-dsh) | 0.15.0（#333，09-08） | 46 skills、2 agents、23 playbooks | `pstack_spawn`（按角色起子 agent）、`pstack_catalog`、overlay 读写、**Settings → pstack** 页、`$DSH_HOME/pstack-dsh.json` | 12 个 test spec、tag v0.2.1–v0.2.3、`HARNESS.md` 逐条引源码、有外部 PR | 落后基线；[dgh52ohp 指出](https://github.com/dgh52ohp125-tech/pstack-dsh) 两个真实 bug：设置保存会把角色映射清空、harness 升级后 `startActivation` 变更导致 spawn 抛错 |
| [dgh52ohp125-tech/pstack-dsh](https://github.com/dgh52ohp125-tech/pstack-dsh) | **0.15.29（88d4751，10-21）** | 63 skills（56 上游 −make-bot-ui + 8 个 team-kit 加值）、12 agents（含 10 个按模型/档位命名的 persona） | `overrides/` 数据层（3 个整文件 + 9 处 patch）、`sync-skills.py`、`capture-seam.py`、`check-upstream.mjs`、`deploy.mjs` | 258 文件、142–156 项测试、CI 每日查上游发版、修了上面两个 bug | 0★、单作者、无 tag/release 历史可核；额外 8 个 skill 来自其自家 open-pstack，不是上游 |
| [tenazur/pstack-dsh](https://github.com/tenazur/pstack-dsh) | #366（09-13） | 47 skills（46 + `pstack-self-check`） | `pstack_spawn`、`pstack_spawn_panel`、`pstack_status`、**pstack Fleet** 设置页 | 正文声称 byte-identical、编译产物已提交、免构建安装 | 0★、10-13 建仓、无测试说明 |
| [wayanjimmy/pstack-dsh](https://github.com/wayanjimmy/pstack-dsh) | 早期 | 21 principles + 20 playbooks（自称 M2 简版） | 原生插件、模型角色设置、skill provider、Web 设置卡 | 1★，最早（08-15） | 快照旧、覆盖不全 |
| [arata-ae/dsh-pstack](https://github.com/arata-ae/dsh-pstack) | 早期 | 未核 | 最小移植 | 08-27 后未更新 | 半成品 |

三个较完整的移植收敛到同一套形态，可直接借鉴结构：

```
DSH plugin bundle (package.json dsh.bundle.patch + cordis.patch.yml)
├── skills/            上游 SKILL.md，调用层改写
├── agents/            2 个上游 agent（部分 fork 加按模型/档位命名的 persona）
├── lib/ 或 src/       宿主侧插件：spawn 工具、catalog、overlay、settings API
└── client bundle      Web 设置页（settings.section 插槽，zh/en）
```

## 三、DSH 生态里可以直接借的件

| 件 | 仓库 / 位置 | 对本移植的用处 |
| --- | --- | --- |
| 官方源码与文档 | [`deepseek-ai/deepseek-harness`](https://github.com/deepseek-ai/deepseek-harness)（MIT，259k★）：`docs/subsystems/*`、`docs/tool-catalog.md`、`packages/*/README.md` | 映射表的权威来源。**本机是 asar 打包，但包内 README 可读**（`[L]`），公开仓库也能按路径取文件 |
| 子代理模型路由插件 | [`CypherNaught-0x/DSH-Subagent-Model-Router`](https://github.com/CypherNaught-0x/DSH-Subagent-Model-Router)、[`green-dalii/dsh-shift-router`](https://github.com/green-dalii/dsh-shift-router) | 前者做"每个子任务路由到不同模型" + 设置页 + `settings.yaml` 热更新；后者做 LLM-judge 双层路由与 failover。**0.2.1 原生 `agentOptions` 已够用，可降级为对照** |
| 插件开发技能 | [`green-dalii/dsh-plugin-dev-skill`](https://github.com/green-dalii/dsh-plugin-dev-skill) | Cordis 心智模型 + `defineTool`/LLM adapter/service/event/bundle 五类插件模板 |
| 订阅登录 peer | [`aa2246740/dsh-oauth-login`](https://github.com/aa2246740/dsh-oauth-login) | 把 ChatGPT/Claude/Grok/Kimi/Antigravity 订阅登录变成 `pi-*` 路由，供角色映射选择 |
| 插件市场 / 分发 | [`dsh-market/dsh-market`](https://github.com/dsh-market/dsh-market)（8.5k★）、[`awesome-dsh-plugin`](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)（20k★）、`awesome-deepseek-harness` 系列 | DSH 侧的"marketplace"是社区市场 + `dsh plugin add`，没有官方 catalog 协议 |
| 预设参考 | [`xiaobright/dsh-anchored-standard`](https://github.com/xiaobright/dsh-anchored-standard) | 两阶段 preset，说明 preset 可定制到什么程度 |

> `dsh-plugin.org` 自称收录 16000+ 插件、全部"verified"，与 GitHub 实际体量不符，按 SEO 聚合站对待。

## 四、已核实的 DSH 平台事实

来自官方 `docs/subsystems/skills.md`、`docs/tool-catalog.md`、本机 asar 内包 README（`[L]`）与三个移植的交叉验证。

| 维度 | 事实 | 对 pstack 的影响 |
| --- | --- | --- |
| skill 身份 | kebab-case `^[a-z0-9]+(?:-[a-z0-9]+)*$`；目录 bundle `<name>/SKILL.md` 或平铺 `<name>.md`；**不支持递归 `**/SKILL.md`** | 56 个 skill 必须是 56 个顶层目录 |
| frontmatter | 本地 provider 认 `disable-model-invocation`、`user-invocable`（缺省都视为 true），另有 `whenToUse` `[L]` | **pstack 全量 `disable-model-invocation: true` 原生支持**，不需要像 omp 那样归一化成 `hide` |
| 本地发现优先级 | `projectRoot/.dsh/skills`(100) → `.agents/skills`(200) → `customSkillDirs`(300) → `~/.dsh/skills`(400) → `~/.agents/skills`(500) → `bundledSkillDir`(600) | 插件内 skills 走 `customSkillDirs`/`bundledSkillDir` 或直接铺用户目录做快速验证 |
| 子代理模型 | 官方 `subagent` 工具支持 `agentOptions{provider, model, reasoningEffort, maxTokens}`、`agentPreset`、`allowedAgentPresets`、`modelSelectionSettings`，并自带 `list_subagent_models` 发现工具 `[L]` | **不必自造 `pstack_spawn`**：角色→模型可以纯配置表达。注意 preset 是否启用这些字段，需实测 |
| 只读/受限子代理 | agent preset 的 `toolFilter` + `allowedAgentPresets`；`toolFilter` 不能放在 tool 行上（加载失败）`[L]` | `pstack-reader`/审查席位可以做成只读 preset，而不是靠 brief 约束 |
| 隔离 / worktree | `dsh-experimental-worktree` + `create_worktree` 存在，但是 **session 级**（"在同一 Session 里继续"），不是 per-child `[L]` | per-child worktree 是真正的缺口，需要自己包 |
| transcript | `dsh-experimental-session-search`（5 个只读全局工具，默认关闭）、`dsh-session-query`、`dsh-session-query-sqlite`、`dsh-tool-session-query`、`dsh-session-log-export` `[L]` | recall/reflect/automate-me 不用自己写读取器，启用并接即可 |
| 编排 | `workflow`（JS 脚本 fan-out）、Agent Teams（9 个工具，`dsh-experimental-agent-team-profile` 已在本机 profile bundles 里）、`ralph`、`create_goal`、`job_*` | 比 omp 强：arena/swarm/autopilot 有更合适的落点 |
| 斜杠命令 | `@deepseek-ai/dsh-commands`：`ctx.commands.register({name, description, input?, run})` `[L]` | 23 个 playbook 可以做成 `/playbook-*` 命令，比"让模型自己读文件"稳 |
| 事件与工具闸门 | `ctx.on('agent/request')`、`tools/pre-execute`（allow/deny/ask）、`tools/execute`、`tools/post-execute`、`tools/result` `[L]` | 可做 per-call 策略，但优先用配置 |
| 插件安装 | `plugin_manager` 工具 / `dsh plugin --profile <p> add <spec>`；包需满足 `engines.dsh` 或 `@deepseek-ai/dsh-*` peer 范围 | 版本范围必须写死 |
| 安装坑 | `github:` / `git+` 规格能装上但不写进 `dsh.profile.bundles`，表现为"declares no dsh.bundle"静默失败（[discussion #656](https://github.com/deepseek-ai/deepseek-harness/discussions/656)）`[W]` | 分发文档必须写清规避方式，或用 `file:`/本地路径挂载验证 |
| skills 路径坑 | provider 指向 `app.asar` 内部会一个 skill 都读不到（[discussion #8649](https://github.com/deepseek-ai/deepseek-harness/discussions/8649)）`[W]` | 装进 profile 的磁盘 `node_modules`，不要指向 asar |
| 文档版本 | 公开讨论与 bug 多数针对 0.1.5–0.1.7；本机运行时是 0.2.1-rc.3 | 网上教程与现成移植的 API 假设普遍落后一行 |

## 五、能力盘点：DSH 已有 vs 需要自建

| pstack 需求 | DSH 0.2.1 现状 | 结论 |
| --- | --- | --- |
| 56 个 skill 可发现、可按名字装载 | 原生（skill provider，非递归） | **配置 + 打包**，无需写代码 |
| `disable-model-invocation` 语义 | 原生 | 不用改写字段 |
| 每角色/面板席位一个模型 | 原生 `agentOptions` + preset + `list_subagent_models` | **配置**；只有"自动按任务难度选模型"才需要插件 |
| 角色档位（effort） | `agentOptions.reasoningEffort`，合法值来自路由 `resolveModelInfo().reasoning.efforts` | **配置**；旧移植的 `agent/request` 方案已过时 |
| 只读子代理 | preset `toolFilter` + 权限 preset（read-only / workspace-write / danger-full-access） | **配置**，但 per-child 粒度需实测 |
| 23 个 playbook 成为可调用入口 | skills + `ctx.commands` | 轻微开发（命令注册） |
| transcript 考古 | `dsh-experimental-session-search` 等 | **启用 + 接线** |
| `/setup-pstack` 交互 | `settings.section` 插槽 + client bundle | 中等开发（Web 面板），已有三家先例 |
| 面板 / 状态看板 | 第二个 spawn 调用 + client 卡片 | 可选，二期 |
| per-child worktree 隔离 | 只有 session 级 worktree | **真正的自建项**，工作量高、风险高 |
| autopilot / orchestrate | Agent Teams + `workflow` + `create_goal` | 无人做，**最大差异化机会** |
| 分发 | plugin bundle + `dsh plugin add` + 社区市场 | **打包工程**，注意 #656 |

## 六、三条路线

| 路线 | 做法 | 成本 | 风险 |
| --- | --- | --- | --- |
| A. 直接 fork dgh52ohp | 已同步 0.15.29、测试最全、seam 设计最好 | 最低 | 来源可信度低；带 8 个非上游 skill，需先审后删；基于 0.2.0-rc 的 API 假设，0.2.1 上要重新验证 |
| B. fork aa2246740 | 文档最好、可当映射表读、有社区 PR | 中：补 10 个 skill、升 0.15.0→0.15.29、修两个已知 bug | `lib/` 是编译产物，改动需能重建；其 `pstack_spawn` 路线在 0.2.1 上属于过度设计 |
| C. 本仓库自建 `pstack-dsh/` | 0.15.29 基线 + PORTING-GUIDE 保真流程 + 原生 seam（不造工具）+ 四分类审查 | 中（比预想低，因为大半是配置） | 仍需真机验证；worktree 隔离要自己写 |

**建议**：走 C，但先用 A 做一次**参考实测**（装进副 profile，跑 `/poteto-mode` 一个真实任务），把"旧移植在 0.2.1 上还能不能跑"变成证据；同时用 B 的 `HARNESS.md` 当映射表校对。这样自建时不是从零，也不是抄一份已过时的设计。

## 七、下一步（待确认）

1. 在本机新建副 profile（如 `pstack-test`），装 A 一份，跑一轮真实调用；不动现有 desktop profile。
2. 按 0.2.1 原生 seam 写一份 DSH 验证清单：`agentOptions` 是否真的接受 model/effort、preset `toolFilter` 是否 per-child 生效、`ctx.commands` 是否让 `/name` 注入、skills 从 bundle 的 `customSkillDirs` 是否加载。
3. 用验证结论写 `docs/harness/dsh.md`，再迁入 0.15.29 基线并机械改写。