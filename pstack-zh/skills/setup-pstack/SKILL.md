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

默认的角色到模型映射见下面第 5 步给出的规则模板。如果 `~/.cursor/rules/pstack-models.mdc` 已经存在，先读取它，把其中的 `# budget` 行和各角色取值当作当前配置；否则从默认配置起步。如果某一行对应的角色不在第 5 步列表里（例如 `how explorer` 或 `why investigators`），说明它是已退役的旧角色，直接删掉。

如果已有规则文件里没有 `# defaults: 2` 这一行，说明它来自旧版配置流程。旧版流程会给每个角色都写一行，因此里面有些值是旧默认值，而不是用户主动选的。凡是匹配 `grok-*` 的都算旧 `slug`。进入第 3 步前，先按下面规则替换这些值：

- 在 `feature, refactoring`、`bug-fix`、`perf-issue`、`hillclimb`、`reflect tooling` 或 `swarm workers` 里的旧 `slug`，换成第 5 步中该角色的默认值。
- 在 `hardest tasks` 里的 `claude-opus-*` 值，换成第 5 步中该角色的默认值。
- 在多模型评审团角色（`arena runners`、`arena cross-judge pool`、`architect runners`、`interrogate reviewers`）里，如果列表恰好包含一个 `claude-opus-*` 项和一个旧 `slug`（顺序不限），整个列表换成第 5 步的默认列表。其他列表里，把每个旧 `slug` 替换成 `claude-opus-5-5-high-fast`。

其余所有值一律视为用户自己的选择并予以保留，包括出现在其他角色里的旧 `slug`，以及所有的 `inherit-parent` 或 `auto`。把你替换了哪些值告知用户。

### 3. 选择预算、映射模型并确认

**(a) 询问推理预算。** 优先使用 AskQuestion，不要用自由文本提问。提供下面四个选项，标签文字保持原样；如果规则文件里已记录预算，顺带报出当前预算。如果没有现成规则文件，说明 `large` 对应的就是 `skill` 默认值。

- `unlimited — max reasoning`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) 按预算换算模型。** 从 `skill` 默认值搭出工作表；如果是重跑配置，保留用户之前改过模型家族、列表或别名（`inherit-parent`、`auto`）的那些角色。模型家族按 **arena** `skill` Phase A 的定义划分，因此 Fable 单独算一个家族。每个角色都有一个目标推理档位，即把该角色默认值的档位按所选预算平移。档位阶梯为 `max` > `xhigh` > `high` > `medium` > `low`，`large` 保持不变，`unlimited` 上调一档，`medium` 下调一档，`small` 下调两档，碰到阶梯两端就停在端点。大多数默认配置都在 `xhigh`，各预算标签里标出的正是它们平移后的落点。把该角色下每个真实 `slug`（包含多模型评审团里的每一项）的档位段改成该角色的目标档位。档位段指的是最后一个词段，或者末尾 `fast` 前面的那个词段。如果拼出来的结果不在检测到的可用 `slug` 里，就改用同一家族里不超过目标档位的最高可用档位；再找不到，就把该角色标为需要人工指定。`inherit-parent` 和 `auto` 不做改动。举个例子，`unlimited` 会把 `claude-opus-5-5-xhigh` 变成 `claude-opus-5-5-max`，把 `claude-opus-5-5-high-fast` 变成 `claude-opus-5-5-xhigh-fast`，同时保持 `claude-fable-5-2-max` 不变。Gemini 最高只到 `high`，所以在 `unlimited` 下回退逻辑会让 `gemini-4-carbon-high` 保持原样。`small` 会把前两者变成 `claude-opus-5-5-medium` 和 `claude-opus-5-5-low-fast`。Fable 5.2 和 Gemini 都没有 fast 版 `slug`，绝不要拼出这类名字。

**(c) 展示各角色配置并确认。** 把每个角色及其对应模型列出来，凡是不在可用集合里的真实 `slug` 都标明需要重新选择，同时列出第 2 步删掉的退役角色行。询问用户是直接按此生效，还是调整特定角色；可选项给出检测到的全部模型，外加 `inherit-parent` 和 `auto`（两者都表示该角色沿用父对话模型，Auto 模式用户靠这个留在 Auto 上）。优先使用 AskQuestion 而不是自由文本。对于多模型评审团角色（`arena runners`、`architect runners`、`interrogate reviewers`），配置值是一个列表，每一项（包括别名项）都会启动一个子代理，列表长度直接决定并行数。`arena cross-judge pool` 也是列表，但 Arena 只跑一位裁判，它会按列表顺序只挑与父会话不同厂商的模型，因此按偏好先后排序。Fable 和其他 Claude 模型同属一家厂商。`inherit-parent` 和 `auto` 绝不充当跨家族裁判。`swarm workers` 是所有工人的默认模型，除非赛马或对比任务单独给各分支指定了不同模型。

### 4. 校验

写入的每一个真实 `slug` 都必须位于已检测到的可用集合内。`inherit-parent` 和 `auto` 始终放行。如果用户选中的真实 `slug` 不可用，停下来重新确认。

### 5. 写入规则文件

写入 `~/.cursor/rules/pstack-models.mdc`，带上 `alwaysApply: true`、`# defaults: 2` 行、写明所选标签和对应档位的 `# budget` 行，以及每个角色一行（角色名与 `poteto-mode` 保持一致）。整份覆盖写入，保证重跑幂等。格式如下：

```
---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# defaults: 2
# budget: large (xhigh)
feature, refactoring: claude-opus-5-5-xhigh
bug-fix: claude-opus-5-5-xhigh
perf-issue: claude-opus-5-5-xhigh
hillclimb: claude-opus-5-5-xhigh
judgment and prose: claude-opus-5-5-xhigh
hardest tasks: claude-fable-5-2-max
reflect tooling: claude-opus-5-5-high-fast
reflect judgment, divergent, synthesizer: claude-opus-5-5-xhigh
arena runners: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-carbon-high
arena cross-judge pool: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-carbon-high
swarm workers: claude-opus-5-5-high-fast
architect runners: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-carbon-high
interrogate reviewers: claude-fable-5-2-high, claude-opus-5-5-high-fast, gemini-4-carbon-high
```

### 6. 确认生效

告知用户规则文件已写入，并将在新会话中生效。以后重新运行本 `skill` 即可更新。

### 7. 询问是否需要本地验证 `skill`（可选）

检查当前项目是否已经有能实操运行真实应用做验证的手段（比如 `verify-*` `skill` 或现成的测试 `harness`）。如果没有，只问一次：「要不要给项目生成一个本地验证 `skill`，让代理能像真实用户一样操作应用来证明改动有效？我可以用 `/create-verification-skill` 帮你生成。」用户同意就调用 `/create-verification-skill`（自动按 pstack 的实际安装位置解析，无论在工作区、用户目录还是插件目录里）；不同意就直接跳过，不要反复推销。

### 8. 询问是否需要形式化验证 `skill`（可选）

检查当前项目是否已经有形式化验证 `skill`（能针对代码跑模型检测器、定理证明或其他形式化验证工具的项目级 `skill`）。如果没有，只问一次：「要不要生成一个形式化验证 `skill`，让代理证明核心不变量在作用域内的所有情况下都成立，而不只是单测覆盖到的那几条路径？我可以用 `/create-formal-verification-skill` 帮你生成。」用户同意就调用 `/create-formal-verification-skill`（同样按 pstack 的实际安装位置解析）；不同意就直接跳过，不要反复推销。
