# pstack → DeepSeek Harness 移植

> **注意：本目录是 pstack 的 DeepSeek Harness 移植版，适配已暂停（2026-10-25），暂不可安装使用。**
>
> - 暂停于 2026-10-25：DSH 适配不再在本仓库环境继续，恢复时从下面「进度」段的未勾选项接着做。
> - 已完成：目录骨架、平台事实记录（见下文表格），以及[现成方案与原生 seam 调研](RESEARCH-prior-art.md)。**未迁入 skill 正文。**
> - 上游原文：[`cursor/plugins` 的 pstack](https://github.com/cursor/plugins/tree/main/pstack)，v0.15.29，commit `88d4751`。
> - 移植方法：仓库根 [`PORTING-GUIDE.md`](../PORTING-GUIDE.md)。同类产物对照 [`pstack-omp/`](../pstack-omp/)（已完成）与 [`pstack-kimi/`](../pstack-kimi/)（已暂停）。
> - 平台差异清单：`docs/harness/dsh.md`（尚未创建，恢复时第一件事）。
> - 现成方案与平台能力调研：[`RESEARCH-prior-art.md`](RESEARCH-prior-art.md)（2026-10-24）。结论：已有 5 个 pstack→DSH 移植；DSH 的 experimental seam（`create_worktree`、Agent Teams、`subagent` 路由字段）足以支撑自建缺失能力。

## 目标平台

| 项 | 值 |
| --- | --- |
| harness | DeepSeek Harness（安装器显示 0.2.1-rc.2；运行时 `@deepseek-ai/dsh-*` 包为 **0.2.1-rc.3**，`@deepseek-ai/cordis` 4.0.5） |
| 安装目录 | `D:\apps\DeepSeek Harness`。渲染进程代码打包在 `resources\app.asar`（非解包目录），原生模块在 `resources\app.asar.unpacked\dsh\node_modules`，内置 skill 样例在 `resources\runtime\office-skills\` |
| 用户目录 | `%USERPROFILE%\.dsh`（即 `DSH_HOME`）：`skills/`、`sessions/`、`plugins/`、`profiles/<profile>/`、`.agent-presets/` |
| 架构 | cordis 插件化 harness。`profiles/<profile>/cordis.yml` 只是空根 `[]`，实际组合来自 `package.json` 的 `dsh.profile.bundles` 加 `cordis.patch.yml`；插件是 npm 包，用 `dsh.bundle.patch` 挂载 |

环境变量方面，DSH 会话里可直接读到 `DSH_HOME`、`DSH_PROFILE`、`DSH_PROFILE_DIR`、`DSH_SESSION_ID`、`DSH_WEB_URL`，这是替代 Cursor 路径硬编码的可靠锚点。

## 动工前已核实的平台事实

这些是决定改写方式的硬事实，尚未构成完整映射表。写 `docs/harness/dsh.md` 时以它们为起点，并逐条用真实调用复核——本仓库的教训 3 要求文档与二进制双证。

| 维度 | DSH 机制 | 与 Cursor / omp 的差异 |
| --- | --- | --- |
| skill 形态 | 目录下 `SKILL.md` + YAML frontmatter，正文即 Markdown。本地 provider 认 `disable-model-invocation`、`user-invocable`（缺省都视为 true）与 `whenToUse`，来源 `docs/subsystems/skills.md` | 与 omp 同构。**pstack 全量 `disable-model-invocation: true` 原生支持**，不需要像 omp 那样归一化成 `hide`——比 omp 更容易 |
| skill 身份 | 名字必须 kebab-case；支持目录 bundle `<name>/SKILL.md` 与平铺 `<name>.md`，**不支持递归 `**/SKILL.md`** | 56 个目录结构可直接搬 |
| skill 装载 | `dsh-skill-filesystem` 发现、`dsh-tool-skill` 目录与装载；本地根按 rank 合并：项目 `.dsh/skills`(100) → `~/.dsh/skills`(400) → bundled(600) | omp 是 provider 扫描 + `skill://` URI。DSH 入口是 `skill` 工具 |
| 子代理 | `subagent` / `subagent_fork`；工具已原生支持 `agentOptions{provider, model, reasoningEffort, maxTokens}`、`agentPreset`、`allowedAgentPresets` 与 `list_subagent_models`（字段是否暴露取决于 preset 组合） | 没有 `subagent_type` 的字符串路由，但**模型可以纯配置指定**，不必像旧移植那样自造 spawn 工具 |
| 只读 / 受限子代理 | agent preset 的 `toolFilter` + `allowedAgentPresets`；`toolFilter` 挂在 preset 上，挂 tool 行会加载失败 | omp 靠 tools 白名单；DSH 靠 preset，能做出真正的只读席位 |
| 模型路由 | 原生 `agentOptions` 指定 provider/model/effort；路由本身在 profile/LLM 适配器层 | omp 的 `modelRoles` 可用 preset 或 `agentOptions` 表达；只有"按任务难度自动选模型"才需要插件 |
| 编排面 | `workflow`（JS 脚本 fan-out）、Agent Teams（9 个工具，experimental；本机 desktop profile 已挂载 `dsh-experimental-agent-team-profile`）、`ralph`、`create_goal`、`job_*`、experimental worktree（**session 级**，非 per-child） | omp 只有 task + async。pstack 的 swarm/arena/autopilot 在 DSH 有更合适的落点，也是最大差异化机会 |
| 会话留存 | `~/.dsh/sessions/`，`DSH_SESSION_ID`/`DSH_PROFILE_DIR` 标识；另有 `dsh-experimental-session-search`、`dsh-session-query-sqlite` 等读取件 | 对应 Cursor 的 `agent-transcripts`，影响 recall、reflect、automate-me、session-pickup——无需自写读取器 |
| 分发 | 没有 omp 式 marketplace。打成 plugin bundle（`package.json` 的 `dsh.bundle.patch` + `cordis.patch.yml`），用 `plugin_manager` 或 `dsh plugin --profile <p> add` 安装；`engines.dsh` / peer 版本不满足会拒绝安装。已知坑：`github:` 规格装上但不写进 `dsh.profile.bundles`（discussion #656） | 版本范围必须写死；分发文档要写清规避方式 |
| 模式与权限 | plan mode（`exit_plan_mode` + `plan:policy` 段）、文件沙箱（本会话 `danger-full-access`）、权限 preset（read-only / workspace-write / danger-full-access） | omp 的 `task.isolation.*` 在 DSH 没有同名开关；隔离只有 session 级 worktree，per-child 是缺口 |

**工具名取决于 agent preset，不能笼统写成"DSH 的工具叫 X"。** 同一台机器上，内置 `minimal` preset 的锚定工具集是 `[bash, str_replace_editor, exit_plan_mode, skill]`（见 `~/.dsh/.agent-presets/liangshen/agent.cordis.yml` 的注释与配置），而当前这个 Lead/Teams preset 暴露的是 `pwsh`、`read`、`write`、`edit`、`glob`、`grep`、`skill`、`subagent`、`spawn_teammate` 等另一套名字。所以映射表第一步必须先锚定"给哪个 preset 用"，否则会重蹈 omp 教训 1 的静默失效。

## 与 omp 移植的关键分叉

omp 那份 `ADAPTATION.md` 里的五张表不能照抄，以下几条需要重新设计：

1. **模型路由**：omp 是 model-per-agent-type + `modelRoles`；DSH 0.2.1 的 `agentOptions`/`agentPreset` 已能表达"每席位一个模型"，所以这里不是缺口，只把配置写进文档即可。
2. **隔离**：omp 的 `isolated: true` 依赖 `task.isolation.enabled`；DSH 的 worktree 是 session 级，per-child 隔离要自己包——这是本移植唯一确定要写代码的缺口。
3. **只读**：omp 靠 tools 白名单；DSH 可以在 agent preset 上挂 `toolFilter`，`pstack-reader` 与审查席位能做成真正的只读 preset，但 per-child 粒度需实测。
4. **能借力的新机制**：`workflow` 的脚本化 fan-out 与 Agent Teams 的持久队友，是 omp 没有的能力；pstack 的 swarm / arena / autopilot 值得优先映射过去，而不是硬套 subagent 循环。
5. **分发**：没有 marketplace，安装路径要么 plugin bundle，要么直铺 skills 目录；PORTING-GUIDE 第 6 步的"两条安装路径各走一次"在这里要换成对应形式，并验证 #656 那个坑。

## 进度

> 暂停于 2026-10-25。恢复时从下面第一个未勾选项接着做。

- [x] 建立目录与分支 `dsh-port`
- [x] 调研现成方案与 DSH 平台能力（见 [`RESEARCH-prior-art.md`](RESEARCH-prior-art.md)）
- [ ] 实测现成移植（A: `dgh52ohp125-tech/pstack-dsh`、B: `aa2246740/pstack-dsh`）于副 profile，拿真实行为当证据
- [ ] 验证 0.2.1 原生 seam：`agentOptions` 是否接受 model/effort、preset `toolFilter` 是否 per-child 生效、`ctx.commands` 斜杠命令、bundle 的 `customSkillDirs` 是否加载 skills
- [ ] 按实测结果定路线（fork A/B 还是自建），再迁入 v0.15.29 原稿作为基线（`skills/`、`agents/`、`docs/`）
- [ ] 写 `docs/harness/dsh.md` 平台差异清单（工具名、子代理字段、模型路由、路径换算、无对应物功能）
- [ ] 机械改写（按文件改，不按概念改）+ 禁词扫描
- [ ] `tools/fidelity` 三个脚本做硬闸门：`check_port.py` problems 0、`outline_compare.py` failures 0
- [ ] 语义审查（MAPPED / LOSS / DRIFT / INVENTION 四分类，两端原文引用）
- [ ] 安装与真实调用验证（skill 命中数 = skill 目录数，agent 能 spawn 且模型落点可证）