# 产物状态

**唯一状态源。** 其它文档提到状态时链接到这里，不要复制表格。

| 目录 | 目标 | 上游基线 | 状态 | 最后确认 | 验证方式 | 决策记录 |
| --- | --- | --- | --- | --- | --- | --- |
| [`pstack-omp/`](../pstack-omp/) | omp | 0.15.32 @ `99b609a` | ✅ 完成，可经 marketplace 分发 | 2026-10-25（增量移植 + 脚本冒烟） | omp 18.12.6：`plugin link` 后 58 个 skill、23 个 playbook、5 个 agent；新进程 `omp -p` 读通 `skill://statechart/SKILL.md` 与 `skill://ketchup-video/SKILL.md`；`statechart render` 出 PNG；三脚本在 [ADAPTATION](../pstack-omp/ADAPTATION.md) 的"验证"一节留有命令与失败对照 | [`ADAPTATION.md`](../pstack-omp/ADAPTATION.md) |
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

omp 的保真闸门（2026-10-25 在 0.15.32 上跑过一遍）：

```bash
python tools/fidelity/diff_bundle.py --port pstack-omp --subdir skills
python tools/fidelity/check_port.py --port pstack-omp --allow url
python tools/fidelity/outline_compare.py --port pstack-omp --subdir skills --ignore bugbot-triage
```

`bugbot-triage` 要 ignore，是因为它被改名为 `review-triage.md`，脚本不认改名；不 ignore 时会报一条 "missing in port"。

dsh / kimi 目前没有可跑的验证命令；恢复或继续时按 [PORTING-GUIDE](../PORTING-GUIDE.md) 第 4–5 步做一次，再把结论写进本表。

## 上游漂移

2026-10-25 升级 pin 到 pstack **0.15.32** @ `99b609a`；`sync.mjs --check` 报两个源在 pin 之后都是 **0** 个提交。0.15.29 → 0.15.32 之间动到 `pstack/` 的 16 个提交已全部落地到 `pstack-omp`（新增 `statechart`、`ketchup-video` 与一批脚本修复，清单见 [ADAPTATION](../pstack-omp/ADAPTATION.md) 的"验证"一节）。

`pstack-zh` 不再是仓库目录：中文译文只作为上游快照存在于 `.upstream/pstack-zh/`（gitignored），由 `sync.mjs` 按 pin 拉取，当前 0.15.29 @ `e447718`，之后没有新提交。它只用于阅读，不进 git、不补译、不作为插件分发。底稿推进后重跑 `node tools/upstream/sync.mjs` 即可；在此之前，中文侧没有 `statechart` 与 `ketchup-video`，要读就读英文原文。

升级上游是独立决定：先改 `UPSTREAM.json` 的 pin，再逐 port 重跑保真闸门与语义审查，不要顺手升级。

## 更新规则

1. 只记**最后确认过的结论**，不记计划。
2. 日期写实际跑命令的那天，不是写文档的那天。
3. 状态变化先改本表，再改相关文档里的指向。
4. 验证方式一栏必须能被人照着复现；做不到就不算已验证。