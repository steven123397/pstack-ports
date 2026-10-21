# benny 自动化意图

> 译自 cursor/plugins 0.15.29 `pstack/automations/benny/FOR_AGENTS.md`。同目录的 `skills/`、`templates/` 子文件自读版保留英文原文，见 `../../../../upstreams/pstack/pstack/automations/benny/`。

## 我想自动化什么

我要两个 Cursor automation，在同一个 Slack issue 频道里配合工作。

### automation 1：分诊 issue 报告

- 触发：有人在配置好的源 Slack 频道里发出一条新的顶层报告时，我要这个 automation 从那份报告启动，并保持原线程坐标不变。
- 行为：读线程和附件，把报告分类为 bug 或性能问题、功能请求、提问或反馈、或改道（reroute），并在路由前先追出可能的责任层。
- tracker：在配置好的 tracker 里查重复；有把握的重复就更新已有工单，只有明确的净新 bug 才建新工单。
- 工具：Slack 线程读写权限、配置好的 tracker 集成、可选的路由表。
- 结果：在源线程里恰好回复一条，附简短结论和 `[benny:bug]`、`[benny:performance]` 或 `[benny:other]` 标记。bug 或性能标记可以带上 tracker URL。
- 边界：绝不许这个 automation 在源频道发根消息。

### automation 2：复现并修复确认过的 bug

- 触发：从同一条新的顶层报告启动，或 setup 时选定的其他受支持触发器，然后等待原线程里出现可信的分诊标记。
- 闸门：有人明确认领修复就停。如果已有的 PR 或已合并的 commit 可能修了这份报告，要做的是验证，而不是提交一个与之竞争的改动。
- 行为：用配置好的 control adapter 和 feature map，通过真实 UI 把确切症状复现两次，截屏、录视频，并做一次只读状态交叉核对。
- 修复：验证已有 PR，不在其上另行改写。复现确认后，可以尝试一次有边界的根因修复；测试便宜就用 TDD；对爆炸半径做冒烟；只有前后对照证明通过时才开草稿 PR。
- 工具：Slack 线程读写权限、仓库与历史访问、草稿 PR 创建、配置好的 tracker、control adapter。
- 结果：在源线程或可选的运维线程里给出证据和验证过的结果，外加可选的草稿 PR。更新要简洁。
- 边界：绝不许这个 automation 在源频道发根消息。

### 共享规则

- 源频道和根线程坐标在整次运行中保持不变。
- 工具机器人和调试机器人只算证据，不算委托或修复归属。
- 允许子代理帮忙，但它们不能往 Slack 发消息，也不能拿到 Slack 凭据。
- 整个 pack 要提交在目标仓库的 `.cursor/automations/benny/`。它的 `SKILL.md` 文件是直接的自动化指令，不是注册的插件 skill。
- pstack 只通过目标仓库已提交的 `.cursor/settings.json` 启用，且只为了共享依赖，如 `how`、`why`、`tdd`、`unslop` 和所需的 principle skills。
- 每个线上 automation prompt 直接读它已提交的运营文件。不要插件缓存路径、不要拷贝摘录、不要 slash-skill 发现。
- 用户自有的配置、feature map、路由表和密钥放在 `.cursor/automations/benny/` 之外，pack 刷新时才不会覆盖它们。
- 频道坐标、tracker 访问、control adapter 或 feature map 缺失或不确定时，两个 automation 都要「故障即停」（fail closed）。
- 只开草稿 PR。不许合并，不许部署。

### 我的配置

- 源 Slack 频道：`<channel>`
- 可选运维频道：`<channel or none>`
- 仓库与默认分支：`<repo>`、`<branch>`
- tracker：`<type, team, project, labels, intake status>`
- 路由表：`<path or none>`
- 分诊身份：`<slack identity>`
- control skill：`<configured skill or adapter>`
- feature map：`<pack 之外、同仓库内的已提交路径，或要改写的行为描述>`
- 模型：`<triage, reproduce, code, media review>`
- 状态 emoji：`<seen, reproducing, reproduced, blocked, fixing, failed, pull request opened>`
- 预算：`<polling, verdict wait, follow-up, repro, rejection, fix>`
- 可选 bot token 能力：`<none, file download, or editable operations status>`

从 [`configuration.example.yaml`](./templates/configuration.example.yaml) 和 [`feature-map.example.md`](./skills/reproduce-and-fix-issues/references/feature-map.example.md) 起步。在 pack 之外拷贝并填写，例如 `.cursor/benny/` 下。密钥值放在密钥管理器或环境变量里。

## 给 agent 的话

人让 Cursor 指向这个文件来进入 setup。不要去找、也不要调用被发现的 benny slash skill。

1. 问 automations 要跑在哪个仓库。
2. 把包含本 `FOR_AGENTS.md` 的目录当作源 pack。
3. 把整个源 pack 合并进 `<target-repository>/.cursor/automations/benny/`。
4. 保留每个仅存在于目标端的文件。绝不删除无关文件，绝不覆盖用户自有的配置、feature map 或路由表。
5. 源管理的路径上已有目标端文件且内容不同时，审阅 diff，合并且不丢弃本地改动。归属不清时，先停下来问，再替换。
6. 确认拷贝过去的 `FOR_AGENTS.md` 和 `skills/setup-benny/SKILL.md` 在目标仓库里存在。
7. 从目标仓库直接读并遵循 `.cursor/automations/benny/skills/setup-benny/SKILL.md`。

我要你把下面这段合并进目标仓库的 `.cursor/settings.json`：

```json
{
	"plugins": {
		"pstack": { "enabled": true }
	}
}
```

保留所有无关设置和插件。现有文件是 jsonc 时，保留注释和合法的 jsonc 语法。

我要从目标仓库起步的一个全新 agent 做验证：确认 pstack 的 `how`、`why`、`tdd`、`unslop` 和 benny 用到的 principle skills 能在项目作用域解析。不要把当前会话或用户作用域安装加载的 skill 算在内。

项目作用域插件不可用、或任何共享依赖解析失败时，停下来并说明失败原因。不要把 `.cursor/automations/benny/skills/` 加进插件 manifest，也不要指望它的文件出现在 slash-skill 列表里。

告诉我：启用任何一个 automation 之前，`.cursor/settings.json`、`.cursor/automations/benny/` 和所有被引用的无密钥配置必须先提交。我明确开口之前，不要创建或更新任何 automation。

首次创建时，用内置 `/automate` 各跑一次：分诊一次、复现修复一次。第一份草稿走完审阅、批准、就绪检查和 Automations 编辑器交接之后，再开始第二份。

把这份意图和最终配置改写进每份草稿。分诊 prompt 必须读并遵循 `.cursor/automations/benny/skills/triage-issue-reports/SKILL.md`。复现 prompt 必须读并遵循 `.cursor/automations/benny/skills/reproduce-and-fix-issues/SKILL.md`。这些仓库相对路径要等 `/automate` 确认它们已提交在 automation 要跑的那个仓库之后才能用。

对已存在的 automation，不要用 `/automate` 去检查或更新它们。验证配置，然后用拷贝过去的 setup 文件里的简短字段清单，让我直接在编辑器里改每个 automation。不要创建重复的。
