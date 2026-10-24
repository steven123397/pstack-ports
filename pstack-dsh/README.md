# pstack → DeepSeek Harness 移植

> **状态：适配刚启动。本目录目前只有这份说明，尚未迁入 skill 正文，不可安装。**
>
> - 上游原文：[`cursor/plugins` 的 pstack](https://github.com/cursor/plugins/tree/main/pstack)，v0.15.29，commit `88d4751`。
> - 移植方法：仓库根 [`PORTING-GUIDE.md`](../PORTING-GUIDE.md)。同类产物对照 [`pstack-omp/`](../pstack-omp/)（已完成）与 [`pstack-kimi/`](../pstack-kimi/)（已暂停）。
> - 平台差异清单：`docs/harness/dsh.md`（尚未创建，下一步第一件事）。

## 目标平台

| 项 | 值 |
| --- | --- |
| harness | DeepSeek Harness 0.2.1（nightly；`DeepSeek Harness.exe` 文件版本 0.2.1.0） |
| 安装目录 | `D:\apps\DeepSeek Harness`。渲染进程代码打包在 `resources\app.asar`（非解包目录），原生模块在 `resources\app.asar.unpacked\dsh\node_modules`，内置 skill 样例在 `resources\runtime\office-skills\` |
| 用户目录 | `%USERPROFILE%\.dsh`（即 `DSH_HOME`）：`skills/`、`sessions/`、`plugins/`、`profiles/<profile>/`、`.agent-presets/` |
| 架构 | cordis 插件化 harness。`profiles/<profile>/cordis.yml` 只是空根 `[]`，实际组合来自 `package.json` 的 `dsh.profile.bundles` 加 `cordis.patch.yml`；插件是 npm 包，用 `dsh.bundle.patch` 挂载 |

环境变量方面，DSH 会话里可直接读到 `DSH_HOME`、`DSH_PROFILE`、`DSH_PROFILE_DIR`、`DSH_SESSION_ID`、`DSH_WEB_URL`，这是替代 Cursor 路径硬编码的可靠锚点。

## 动工前已核实的平台事实

这些是决定改写方式的硬事实，尚未构成完整映射表。写 `docs/harness/dsh.md` 时以它们为起点，并逐条用真实调用复核——本仓库的教训 3 要求文档与二进制双证。

| 维度 | DSH 机制 | 与 Cursor / omp 的差异 |
| --- | --- | --- |
| skill 形态 | 目录下 `SKILL.md` + YAML frontmatter（`name`、`description`），正文即 Markdown。样例见 `resources\runtime\office-skills\office-docx\SKILL.md` | 与 omp 同构。frontmatter 字段集合需要单独确认，`disable-model-invocation` 在 DSH 的对应物未知 |
| skill 装载 | `dsh-skill-filesystem` 负责发现、`dsh-tool-skill` 负责目录与装载；原生目录 `~/.dsh/skills/`（当前为空）；插件包也能全局注册 skill | omp 是 provider 扫描 + `skill://` URI。DSH 的调用入口是 `skill` 工具（见本会话 catalog） |
| 子代理 | `subagent`（`context: fresh`）与 `subagent_fork`（继承父会话上下文），参数含 `prompt`/`description`/`cwd`，支持后台与续聊 | 没有 Cursor 的 `subagent_type`，没有 `readonly`，**没有 per-spawn 的 `model`** |
| 编排面 | 除 subagent 外还有：`workflow`（JS 脚本 fan-out）、Agent Teams（`spawn_teammate` + `team_task_*` + `send_message`/`wait_agent`）、`ralph`、`create_goal`、后台任务 `run_in_background` + `job_*` | omp 只有 task + async，没有 workflow / teams / goal。pstack 的 swarm、arena、autopilot 可能更适合映射到这三者之一 |
| 模型路由 | spawn 不接受 `model` 参数，路由在 profile 与模型配置层 | omp 的 `modelRoles`（`@pstack-fast` 等）没有直接等价物。"每席位一个模型"需要新方案 |
| 会话留存 | `~/.dsh/sessions/`，会话由 `DSH_SESSION_ID` 标识 | 对应 Cursor 的 `agent-transcripts`，影响 recall、reflect、automate-me、session-pickup |
| 分发 | **没有 marketplace**。只能做成 plugin bundle，或直接把 `skills/` 铺进 `~/.dsh/skills/` | omp 走 `.omp-plugin/marketplace.json` catalog |
| 模式与权限 | plan mode（`exit_plan_mode` + `plan:policy` 段）、文件沙箱（本会话为 `danger-full-access`）、审批策略（本会话审批被禁用） | omp 的 `task.isolation.*` 在 DSH 没有同名开关，需实测落点 |

**工具名取决于 agent preset，不能笼统写成"DSH 的工具叫 X"。** 同一台机器上，内置 `minimal` preset 的锚定工具集是 `[bash, str_replace_editor, exit_plan_mode, skill]`（见 `~/.dsh/.agent-presets/liangshen/agent.cordis.yml` 的注释与配置），而当前这个 Lead/Teams preset 暴露的是 `pwsh`、`read`、`write`、`edit`、`glob`、`grep`、`skill`、`subagent`、`spawn_teammate` 等另一套名字。所以映射表第一步必须先锚定"给哪个 preset 用"，否则会重蹈 omp 教训 1 的静默失效。

## 与 omp 移植的关键分叉

omp 那份 `ADAPTATION.md` 里的五张表不能照抄，以下几条需要重新设计：

1. **模型路由**：omp 是 model-per-agent-type + `modelRoles`；DSH 是 profile 级路由。arena / interrogate 的多模型面板要在 DSH 里重新找承载方式（候选：多个 agent preset、或 `subagent` 的 provider 差异）。
2. **隔离**：omp 的 `isolated: true` 依赖 `task.isolation.enabled`，DSH 对应的是沙箱策略与审批，语义不同；autopilot / swarm 的"先验证后落地"顺序要重新实测。
3. **只读**：DSH 的 subagent 没有工具级只读，`pstack-reader` 这类角色只能靠 brief 约束加 `git status` 复核（omp 教训 8 的同构问题）。
4. **能借力的新机制**：`workflow` 的脚本化 fan-out 与 Agent Teams 的持久队友，是 omp 没有的能力；pstack 的 swarm / arena / interrogate 值得优先映射过去，而不是硬套 subagent 循环。
5. **分发**：没有 marketplace，安装路径要么 plugin bundle，要么直铺 skills 目录；PORTING-GUIDE 第 6 步的"两条安装路径各走一次"在这里要换成对应形式。

## 进度

- [x] 建立目录与分支 `dsh-port`
- [ ] 迁入 v0.15.29 原稿作为基线（`skills/`、`agents/`、`docs/`）
- [ ] 写 `docs/harness/dsh.md` 平台差异清单（工具名、子代理字段、模型路由、路径换算、无对应物功能）
- [ ] 机械改写（按文件改，不按概念改）+ 禁词扫描
- [ ] `tools/fidelity` 三个脚本做硬闸门：`check_port.py` problems 0、`outline_compare.py` failures 0
- [ ] 语义审查（MAPPED / LOSS / DRIFT / INVENTION 四分类，两端原文引用）
- [ ] 安装与真实调用验证（skill 命中数 = skill 目录数，agent 能 spawn 且模型落点可证）