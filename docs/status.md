# 产物状态

**唯一状态源。** 其它文档提到状态时链接到这里，不要复制表格。

| 目录 | 目标 | 上游基线 | 状态 | 最后确认 | 验证方式 | 决策记录 |
| --- | --- | --- | --- | --- | --- | --- |
| [`pstack-omp/`](../pstack-omp/) | omp | 0.15.29 @ `88d4751` | ✅ 完成，可经 marketplace 分发 | 2026-10-22（运行验证） | omp 1.4.3 上完成安装、skill 调用与四个 agent 的模型落点验证；验证脚本与证据未入库（已清理） | [`ADAPTATION.md`](../pstack-omp/ADAPTATION.md) |
| [`pstack-dsh/`](../pstack-dsh/) | DeepSeek Harness | 0.15.29 @ `88d4751` | 🚧 进行中：只有骨架与调研，无 skill 正文 | 2026-10-24（仅调研） | 未开始；清单见 [`RESEARCH-prior-art.md`](../pstack-dsh/RESEARCH-prior-art.md) 第七节 | [`README.md`](../pstack-dsh/README.md) |
| [`pstack-kimi/`](../pstack-kimi/) | Kimi Code | 0.15.29 @ `88d4751` | ⏸ 暂停（2026-10-24） | 2026-10-24 | 无运行验证；迁移了基线并改写了 3 个入口，其余未完成 | [`README.md`](../pstack-kimi/README.md) 首段 |
| [`pstack-zh/`](../pstack-zh/) | 阅读用中文版（非插件） | 0.15.29 @ `88d4751` | ✅ 完成 | 未独立复核（按 README 自述记录于 2026-10-24） | 无脚本闸门；README 自述已对齐 0.15.29 | [`README.md`](../pstack-zh/README.md) |

状态取值只有四个：`⏸ 暂停`、`🚧 进行中`、`✅ 完成`、`🗑 归档`。不做"基本完成"这种中间态。

## 再生命令

上游与计数（改上游后重跑）：

```bash
node tools/upstream/sync.mjs          # 按 UPSTREAM.json 的 pin 拉到 .upstream/
node tools/upstream/sync.mjs --check  # 只报告各源在 pin 之后有多少新提交
git ls-files 'pstack-*/skills/*/SKILL.md' | wc -l
```

omp 的保真闸门（运行验证已于 2026-10-22 做过一次，脚本未保留）：

```bash
python tools/fidelity/check_port.py --port pstack-omp --allow url
python tools/fidelity/outline_compare.py --port pstack-omp --subdir skills --ignore bugbot-triage
```

dsh / kimi 目前没有可跑的验证命令；恢复或继续时按 [PORTING-GUIDE](../PORTING-GUIDE.md) 第 4–5 步做一次，再把结论写进本表。

## 上游漂移

截至 2026-10-25，`cursor/plugins` 的 main 在 pin 之后有 **67** 个提交（`node tools/upstream/sync.mjs --check` 可复现）。升级上游是独立决定：先改 `UPSTREAM.json` 的 pin，再逐 port 重跑保真闸门与语义审查，不要顺手升级。

## 更新规则

1. 只记**最后确认过的结论**，不记计划。
2. 日期写实际跑命令的那天，不是写文档的那天。
3. 状态变化先改本表，再改相关文档里的指向。
4. 验证方式一栏必须能被人照着复现；做不到就不算已验证。