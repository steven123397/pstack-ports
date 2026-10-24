# pstack-ports

pstack 是 Lauren Tan（poteto）为 Cursor 写的一套工程方法论：56 个 skill、23 个 playbook、24 条原则、2 个子代理，核心是 `/poteto-mode`。它的价值不在某个平台的 API，而在**流程与原则**——所以它可以被搬走。

本仓库是 pstack 跨 agent harness 适配的**统一存放处**。每适配一个平台，这里多一份可安装的产物、一份平台差异清单、一次保真验证；方法本身沉淀成一份可复用指南。

- 上游：`cursor/plugins` 的 `pstack`，v0.15.29（commit `88d4751`），MIT。基线锁定在 [`UPSTREAM.json`](UPSTREAM.json)。
- 方法：[`PORTING-GUIDE.md`](PORTING-GUIDE.md)（六步流程 + 十条教训）。
- 状态：[`docs/status.md`](docs/status.md)（唯一状态源，含每个产物的验证方式）。

## 产物矩阵

| 目录 | 目标 | 状态 | 读哪里 |
| --- | --- | --- | --- |
| [`pstack-omp/`](pstack-omp/) | omp | ✅ 完成，可经 marketplace 分发 | [`ADAPTATION.md`](pstack-omp/ADAPTATION.md)、[`docs/harness/omp.md`](pstack-omp/docs/harness/omp.md) |
| [`pstack-dsh/`](pstack-dsh/) | DeepSeek Harness | 🚧 进行中（骨架 + 调研） | [`README.md`](pstack-dsh/README.md)、[`RESEARCH-prior-art.md`](pstack-dsh/RESEARCH-prior-art.md) |
| [`pstack-kimi/`](pstack-kimi/) | Kimi Code | ⏸ 暂停（2026-10-24） | [`README.md`](pstack-kimi/README.md) 首段、[`docs/harness/kimicode.md`](pstack-kimi/docs/harness/kimicode.md) |
| [`pstack-zh/`](pstack-zh/) | 阅读用中文版（不是 port） | ✅ 完成 | [`README.md`](pstack-zh/README.md) |

`pstack-zh/` 是上游的中文自读版，用于理解每个 skill 在做什么，不作为插件分发；它和 port 同层只是为了方便对照。

## 怎么读

- **想装来用**：看目标平台的产物目录，omp 走 [`pstack-omp/ADAPTATION.md`](pstack-omp/ADAPTATION.md) 的分发章节；dsh 尚未可装。
- **想理解 pstack 本身**：从 [`pstack-zh/README.md`](pstack-zh/README.md) 的阅读顺序开始，或直接读 `pstack-zh/skills/poteto-mode/SKILL.md`。
- **想读懂移植怎么做**：[`PORTING-GUIDE.md`](PORTING-GUIDE.md)。
- **想新增一个平台**：先读 [`docs/README.md`](docs/README.md) 的文档地图，再按 PORTING-GUIDE 的六步走。

## 目录结构

按职责分四层，不要混用：

| 层 | 路径 | 放什么 | 不该放什么 |
| --- | --- | --- | --- |
| 仓库层 | `README.md`、`UPSTREAM.json`、`docs/status.md` | 总入口、上游 pin、状态矩阵 | 单个平台的映射细节 |
| 方法层 | `PORTING-GUIDE.md`、`tools/fidelity/`、`verify/` | 可复用的流程、脚本、验证资产 | 与某个平台绑定的命令 |
| 产物层 | `pstack-<platform>/` | 自包含、可直接分发的插件包：`skills/`、`agents/`、平台清单、包内映射表与决策记录 | 仓库级索引 |
| 翻译层 | `pstack-zh/` | 上游中文译文与教程 | 适配决策 |

产物层每个目录都**自包含**：它要能被单独打包分发，所以允许与其它 port 重复（`skills/` 是逐份副本）。重复是交付形态，不是结构问题；差异靠 `tools/fidelity` 对照上游量化。

## 保真与验证

移植的质量判断不靠感觉，靠三个只读脚本（用法见 [`tools/fidelity/README.md`](tools/fidelity/README.md)）：

```bash
python tools/fidelity/diff_bundle.py --upstream <上游根> --port pstack-<platform> --subdir skills --out %TEMP%/fidelity
python tools/fidelity/check_port.py --port pstack-<platform> --allow url
python tools/fidelity/outline_compare.py --upstream <上游根> --port pstack-<platform> --subdir skills
```

`check_port.py` 的 `problems 0` 与 `outline_compare.py` 的 `failures 0` 是硬闸门；改动行数只是定位信号。平台侧的运行验证资产见 [`verify/README.md`](verify/README.md)。

## 新增一个平台的最小动作

1. 更新 [`UPSTREAM.json`](UPSTREAM.json)（只在升级上游时）。
2. 建 `pstack-<platform>/`，先写 `docs/harness/<platform>.md` 平台差异清单，再动 skill 正文。
3. 迁入上游原稿作基线，按文件机械改写，跑禁词扫描。
4. 跑 `tools/fidelity` 三个脚本，两个硬闸门清零。
5. 按语义切片做语义审查（四分类 rubric，两端原文引用）。
6. 装一次、真实调用一次，把验证资产放到 `verify/<platform>/`，状态写进 [`docs/status.md`](docs/status.md)。

## 许可

上游 pstack 归 Lauren Tan，MIT。各产物的 `LICENSE` 随目录分发；本仓库的移植层与文档沿用同一许可。