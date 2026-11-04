# 产物状态

**唯一状态源。** 其它文档提到状态时链接到这里，不要复制表格。

| 目录 | 目标 | 上游基线 | 状态 | 最后确认 | 验证方式 | 决策记录 |
| --- | --- | --- | --- | --- | --- | --- |
| [`pstack-omp/`](../pstack-omp/) | omp | 0.15.36 @ `fd268b8` | ✅ 完成，可经 marketplace 分发 | 2026-11-04（增量移植 + 保真闸门 + statechart 启动冒烟） | omp 18.13.1：58 个 skill、23 个 playbook、5 个 agent；`omp plugin doctor pstack-omp` 4 ok / 0 error；三脚本 `problems 0` / `failures 0` / `721 / 29113`；Node 24.15 下 `sh statechart` 打印 `Give one SPEC.tla.`（无参数用法错误，退出 2），证明启动器已把 TypeScript 交给 Node；statechart 纯 TS 单测 50/50（CRLF 归一为 LF 后）。命令与失败对照见 [ADAPTATION](../pstack-omp/ADAPTATION.md) 的"验证"一节 | [`ADAPTATION.md`](../pstack-omp/ADAPTATION.md) |
| [`pstack-dsh/`](../pstack-dsh/) | DeepSeek Harness | 0.15.29 @ `88d4751`（落后仓库 pin） | ⏸ 暂停（2026-10-25）：只有骨架与调研，无 skill 正文 | 2026-10-25 | 未开始；清单见 [`RESEARCH-prior-art.md`](../pstack-dsh/RESEARCH-prior-art.md) 第七节 | [`README.md`](../pstack-dsh/README.md) |
| [`pstack-kimi/`](../pstack-kimi/) | Kimi Code | 0.15.29 @ `88d4751`（落后仓库 pin） | ⏸ 暂停（2026-10-24） | 2026-10-24 | 无运行验证；迁移了基线并改写了 3 个入口，其余未完成 | [`README.md`](../pstack-kimi/README.md) 首段 |

状态取值只有四个：`⏸ 暂停`、`🚧 进行中`、`✅ 完成`、`🗑 归档`。不做"基本完成"这种中间态。

## 再生命令

上游与计数（改上游后重跑）：

```bash
node tools/upstream/sync.mjs          # 按 UPSTREAM.json 的 pin 拉到 .upstream/
node tools/upstream/sync.mjs --check  # 只报告各源在 pin 之后有多少新提交
git ls-files 'pstack-*/skills/*/SKILL.md' | wc -l
```

omp 的保真闸门（2026-11-04 在 0.15.36 上跑过一遍）：

```bash
python tools/fidelity/diff_bundle.py --port pstack-omp --subdir skills
python tools/fidelity/check_port.py --port pstack-omp --allow url
python tools/fidelity/outline_compare.py --port pstack-omp --subdir skills --ignore bugbot-triage
```

`bugbot-triage` 要 ignore，是因为它被改名为 `review-triage.md`，脚本不认改名；不 ignore 时会报一条 "missing in port"。

dsh / kimi 目前没有可跑的验证命令；恢复或继续时按 [PORTING-GUIDE](../PORTING-GUIDE.md) 第 4–5 步做一次，再把结论写进本表。

## 上游漂移

2026-11-04 升级 pin 到 pstack **0.15.36** @ `fd268b8`（2026-11-03）。0.15.32 → 0.15.36 之间动到 `pstack/` 的 7 个提交已全部落地到 `pstack-omp`：`statechart` 从一组 `.mjs` 脚本换成 TypeScript 编译器（连同其测试语料保留，仅把换行规范为 LF），`orchestrate` 改成 agentic 并删除 `scripts/orch/`，`interrogate` 改为 adversaries 用一次真实运行证明每条发现、lead 只保留可复现的，同时删除 reviewer/rubric/lead-judgment 四个 reference；`arena` 的 cross-judge 改为只从另一个模型家族选、选不到就跳过；另有 poteto-mode 首条消息复述目标、autopilot 阻塞规则、ketchup-video 字幕、explain-the-number 先写决策等。三个保真脚本复跑：`check_port` problems 0、`outline_compare` failures 0、`diff_bundle` 721 / 29113。`cursor-plugins` 现在 pin 与 origin/HEAD 一致，0 个新提交；`pstack-zh` 仍停在 0.15.29，`pstack-claude` / `open-pstack` 是只读参考快照，未跟随。

这次 `interrogate` 的改动与作者 2026-11-03 在 X 上的公开说法一致：对抗式评审多数是浪费 token，更看重经验验证加形式验证；她已经减少 pstack 里 `interrogate` 的使用，长期可能整个移除。0.15.36 尚未删除该 skill，所以 port 保留它，只按新语义改写（发现必须由运行证明，报告只列可复现项）。

2026-10-27 参考快照调整：移除 `pstack-zcode`，加入 `pstack-claude`（michael-denyer，0.9.103，跟踪上游 0.15.32 @ `e73df47`）与 `open-pstack`（ericlitman，1.16.0，跟踪上游 0.15.29 @ `88d4751`）。两者只读，不是任何 port 的移植基线。同日 `sync.mjs --check`：`cursor-plugins` 在 pin 之后 **21** 个提交（origin/main `ab69380`），另外三个参考/译文源均为 **0**。pin 未移动；升级上游仍是独立决定。

2026-10-25 升级 pin 到 pstack **0.15.32** @ `99b609a`；`sync.mjs --check` 报两个源在 pin 之后都是 **0** 个提交。0.15.29 → 0.15.32 之间动到 `pstack/` 的 16 个提交已全部落地到 `pstack-omp`（新增 `statechart`、`ketchup-video` 与一批脚本修复，清单见 [ADAPTATION](../pstack-omp/ADAPTATION.md) 的"验证"一节）。

`pstack-zh` 不再是仓库目录：中文译文只作为上游快照存在于 `.upstream/pstack-zh/`（gitignored），由 `sync.mjs` 按 pin 拉取，当前 0.15.29 @ `e447718`，之后没有新提交。它只用于阅读，不进 git、不补译、不作为插件分发。底稿推进后重跑 `node tools/upstream/sync.mjs` 即可；在此之前，中文侧没有 `statechart` 与 `ketchup-video`，要读就读英文原文。

升级上游是独立决定：先改 `UPSTREAM.json` 的 pin，再逐 port 重跑保真闸门与语义审查，不要顺手升级。

## 更新规则

1. 只记**最后确认过的结论**，不记计划。
2. 日期写实际跑命令的那天，不是写文档的那天。
3. 状态变化先改本表，再改相关文档里的指向。
4. 验证方式一栏必须能被人照着复现；做不到就不算已验证。