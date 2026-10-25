# 文档地图

仓库里文档不少，但职责只有几种。先看这张表，再决定读哪份；不确定时以本表为准，不以目录位置猜。

| 文档 | 读者 | 职责 | 何时更新 |
| --- | --- | --- | --- |
| [`README.md`](../README.md) | 所有人 | 项目定位、产物矩阵、目录分层、快速开始 | 新增或关闭一个 port 时 |
| [`UPSTREAM.json`](../UPSTREAM.json) | 维护者、脚本 | 上游 pin（版本、commit、本地镜像、计数），机器可读 | 升级上游时，先改这里 |
| [`status.md`](status.md) | 维护者 | **唯一状态源**：每个产物的状态、最后确认时间、验证方式、再生命令 | 每次验证后 |
| [`PORTING-GUIDE.md`](../PORTING-GUIDE.md) | 新移植者 | 方法论：三种移植姿态、六步流程、十条教训、未解项 | 方法本身变化时 |
| [`tools/fidelity/README.md`](../tools/fidelity/README.md) | 执行移植的人 | 三个只读脚本的用法与通过标准 | 脚本变化时 |
| `pstack-<platform>/docs/harness/<platform>.md` | 模型与执行者（产物内） | 平台差异清单：工具名、子代理字段、模型路由、路径、跳过策略。是**产物的一部分**，随包分发 | 平台机制变化时 |
| `pstack-<platform>/ADAPTATION.md` | 维护者（产物内） | 该平台的适配决策记录、验证结论、已知限制 | 决策变化时 |
| `pstack-zh/README.md` | 中文读者 | 译文说明、相对底稿的改动、阅读顺序 | 上游译文更新时 |

## 三条写法约定

1. **状态只写在 `docs/status.md`。** 其它文档提到状态时用链接，不复制表格——复制就会漂移（[PORTING-GUIDE](../PORTING-GUIDE.md) 教训 9：自述文档会腐化）。
2. **计数要配再生命令。** 任何"56 个 skill""23 个 playbook"旁边能跑出同样的数，否则不写具体数字。
3. **平台细节留在产物里，不外提。** omp 的 `skills` 字段写法不该出现在根 README；仓库层只讲跨平台的部分。

## 已知的重复与例外

- 每个 `pstack-<platform>/skills/` 都是 56 个 skill 的完整副本。这是**交付形态**（包要能独立分发），不是重复建设；差异由 `tools/fidelity` 对照上游量化。
- `pstack-zh/docs/harness/claude-code.md` 是上游官方适配文档的译文，属于译文内容，不是本仓库对 Claude Code 的移植结论。
- `.omp-plugin/marketplace.json` 必须在 omp 约定的路径上才能被发现，看起来像"藏起来的目录"，实为平台约定；作用在根 README 的产物矩阵里有指向。