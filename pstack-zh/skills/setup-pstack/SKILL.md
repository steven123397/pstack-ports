---
name: setup-pstack
description: "配置 pstack 各角色使用的模型与推理预算。自动检测当前可用模型，并写入一条总是生效的规则文件来覆盖 skill 默认配置。适用于 /setup-pstack、「配置 pstack 模型」、「调整 pstack 预算」或修改 pstack 模型选择。"
---

# Setup pstack

写入 `~/.cursor/rules/pstack-models.mdc`，通过这条 `always-applied rule`（全局常驻生效的规则文件）为 pstack 的各个角色指定模型。

## 执行步骤

### 1. 检测可用模型

枚举当前会话里能传给 `Task` 子代理的模型 `slug`，这是最可靠的来源。如果 Cursor 同时提供了能列出用户已授权模型的 API 或 CLI，优先用它来补全列表。如果完全检测不到，请用户直接贴出他们可用的 `slug`。绝不要写入未经确认可用的真实 `slug`。别名 `inherit-parent` 和 `auto` 始终合法，哪怕它们不会出现在检测出的 `slug` 列表里。

### 2. 读取当前配置

默认的角色到模型映射见下面第 5 步给出的规则模板。如果 `~/.cursor/rules/pstack-models.mdc` 已经存在，先读取它，把其中的 `# budget` 行和各角色取值当作当前配置；否则从默认配置起步。如果某一行对应的角色不在第 5 步列表里（例如 `hardest tasks`、`architect runners`、`reflect tooling` 或 `why investigators`），说明它是已退役的旧角色，直接删掉。

早期默认配置先后把其他 Gemini 模型和 `gemini-4-neon-high` 放进评审团席位。因此只要规则文件里任意评审团角色（`arena runners`、`arena cross-judge pool`、`interrogate reviewers`）出现 `gemini-4-neon-high`，或者非 `gemini-4-neon-*` 的 `gemini-4-*` 条目，都视为旧默认值，统一替换为 `gemini-4-neon-xhigh`。其他档位的 Gemini 4 Neon 条目视为用户主动选择并予以保留。把你替换了哪些条目告知用户。

如果已有规则文件里没有 `# defaults: 3` 这一行，说明它来自旧版配置流程。旧版流程会给每个角色都写一行，因此里面有些值是旧默认值，而不是用户主动选的。进入第 3 步前，先按下面规则替换这些值：

- 如果 `arena cross-judge pool` 列表恰好包含一个 `claude-fable-*`、一个 `claude-opus-*` 和一个 `gemini-*`（顺序不限），直接换成第 5 步中该角色的默认列表。Fable 和 Opus 同属一家厂商，Fable 条目能评的场合 Opus 同样能评。
- `# budget: unlimited` 改为 `large`，因为现在任何角色都不超过 `xhigh`。
- 如果规则文件连 `# defaults: 2` 这一行也没有，凡是匹配 `grok-*` 的都算旧 `slug`。出现在 `feature, refactoring`、`bug-fix`、`perf-issue`、`hillclimb` 或 `swarm workers` 里的旧 `slug`，换成第 5 步中该角色的默认值。在评审团角色（`arena runners`、`arena cross-judge pool`、`interrogate reviewers`）里，如果列表恰好包含一个 `claude-opus-*` 项和一个旧 `slug`（顺序不限），整个列表换成第 5 步的默认列表。其他列表里，每个旧 `slug` 都替换成 `claude-opus-5-5-high-fast`。

其余所有值一律视为用户自己的选择并予以保留，包括出现在其他角色里的旧 `slug`，以及所有的 `inherit-parent` 或 `auto`。把你替换了哪些值告知用户。

### 3. 选择预算、映射模型并确认

**(a) 询问推理预算。** 优先使用 AskQuestion，不要用自由文本提问。提供下面三个选项，标签文字保持原样；如果规则文件里已记录预算，顺带报出当前预算。如果没有现成规则文件，说明 `large` 对应的就是 `skill` 默认值。

- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) 按预算换算模型。** 从 `skill` 默认值搭出工作表；如果是重跑配置，保留用户之前改过模型家族、列表或别名（`inherit-parent`、`auto`）的那些角色。模型家族按 **arena** `skill` Phase A 的定义划分，因此 Fable 单独算一个家族。每个角色都有一个目标推理档位，即把该角色默认值的档位按所选预算平移。档位阶梯为 `xhigh` > `high` > `medium` > `low`，`large` 保持不变，`medium` 下调一档，`small` 下调两档。任何角色都不超过 `xhigh`，目标触底时停在底端。大多数默认配置都在 `xhigh`，各预算标签里标出的正是它们平移后的落点。把该角色下每个真实 `slug`（包含评审团里的每一项）的档位段改成该角色的目标档位。档位段指的是最后一个词段，或者末尾 `fast` 前面的那个词段。如果拼出来的结果不在检测到的可用 `slug` 里，就改用同一家族里不超过目标档位的最高可用档位；再找不到，就把该角色标为需要人工指定。`inherit-parent` 和 `auto` 不做改动。因此，`medium` 会把 `claude-opus-5-5-xhigh-fast` 变成 `claude-opus-5-5-high-fast`，把 `claude-opus-5-5-high-fast` 变成 `claude-opus-5-5-medium-fast`；`small` 会把它们分别变成 `claude-opus-5-5-medium-fast` 和 `claude-opus-5-5-low-fast`。Opus 5.5 始终使用 `-fast` 版本，所以每个 Opus 5.5 取值都以 `-fast` 结尾。Fable 5.2 和 Gemini 都没有 fast 版 `slug`，绝不要拼出这类名字。Gemini 4 Neon 的 `slug` 从 `low` 到 `xhigh`，没有 `max` 或 `fast` 版本，因此它的席位默认跑在最高档 `gemini-4-neon-xhigh`。评审团角色里的 Gemini 4 Neon 条目使用独立的目标档位，即从 `xhigh` 按预算平移：`large` 保持 `gemini-4-neon-xhigh`，`medium` 写入 `gemini-4-neon-high`，`small` 写入 `gemini-4-neon-medium`。

**(c) 展示各角色配置并确认。** 把每个角色及其对应模型列出来，凡是不在可用集合里的真实 `slug` 都标明需要重新选择，同时列出第 2 步删掉的退役角色行。询问用户是直接按此生效，还是调整特定角色；可选项给出检测到的 `xhigh` 及以下模型，外加 `inherit-parent` 和 `auto`（两者都表示该角色沿用父对话模型，Auto 模式用户靠这个留在 Auto 上）。优先使用 AskQuestion 而不是自由文本。对于多模型评审团角色（`arena runners`、`interrogate reviewers`），配置值是一个列表，每一项（包括别名项）都会启动一个子代理，列表长度直接决定并行数。`arena cross-judge pool` 也是列表，但 Arena 只跑一位裁判，它会按列表顺序只挑与父会话不同厂商的模型，因此按偏好先后排序。Fable 和其他 Claude 模型同属一家厂商。`inherit-parent` 和 `auto` 绝不充当跨家族裁判。`swarm workers` 是所有工人的默认模型，除非赛马或对比任务单独给各分支指定了不同模型。

### 4. 校验

写入的每一个真实 `slug` 都必须位于已检测到的可用集合内，且档位在 `xhigh` 或以下。`inherit-parent` 和 `auto` 始终放行。如果用户选中的真实 `slug` 不可用，停下来重新确认。

### 5. 写入规则文件

写入 `~/.cursor/rules/pstack-models.mdc`，带上 `alwaysApply: true`、`# defaults: 3` 行、写明所选标签和对应档位的 `# budget` 行，以及每个角色一行（角色名与 `poteto-mode` 保持一致）。整份覆盖写入，保证重跑幂等。格式如下：

```
---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model` and spawn `generalPurpose`). Alias entries in a panel list still count toward its fan-out.
# defaults: 3
# budget: large (xhigh)
feature, refactoring: claude-opus-5-5-xhigh-fast
bug-fix: claude-opus-5-5-xhigh-fast
perf-issue: claude-opus-5-5-xhigh-fast
hillclimb: claude-opus-5-5-xhigh-fast
judgment and prose: claude-opus-5-5-xhigh-fast
arena runners: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-neon-xhigh
arena cross-judge pool: claude-opus-5-5-high-fast, gemini-4-neon-xhigh
swarm workers: claude-opus-5-5-high-fast
interrogate reviewers: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-neon-xhigh
```

### 6. 确认生效

告知用户规则文件已写入，并将在新会话中生效。以后重新运行本 `skill` 即可更新。

### 7. 询问是否需要本地验证 `skill`（可选）

检查当前项目是否已经有能实操运行真实应用做验证的手段（比如 `verify-*` `skill` 或现成的测试 `harness`）。如果没有，只问一次：「要不要给项目生成一个本地验证 `skill`，让代理能像真实用户一样操作应用来证明改动有效？我可以用 `/create-verification-skill` 帮你生成。」用户同意就调用 `/create-verification-skill`（自动按 pstack 的实际安装位置解析，无论在工作区、用户目录还是插件目录里）；不同意就直接跳过，不要反复推销。

### 8. 询问是否需要形式化验证 `skill`（可选）

检查当前项目是否已经有形式化验证 `skill`（能针对代码跑模型检测器、定理证明或其他形式化验证工具的项目级 `skill`）。如果没有，只问一次：「要不要生成一个形式化验证 `skill`，让代理证明核心不变量在作用域内的所有情况下都成立，而不只是单测覆盖到的那几条路径？我可以用 `/create-formal-verification-skill` 帮你生成。」用户同意就调用 `/create-formal-verification-skill`（同样按 pstack 的实际安装位置解析）；不同意就直接跳过，不要反复推销。
