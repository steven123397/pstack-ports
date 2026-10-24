# 产物状态

**唯一状态源。** 其它文档提到状态时链接到这里，不要复制表格。

| 目录 | 目标 | 上游基线 | 状态 | 最后确认 | 验证方式 | 决策记录 |
| --- | --- | --- | --- | --- | --- | --- |
| [`pstack-omp/`](../pstack-omp/) | omp | 0.15.29 @ `88d4751` | ✅ 完成，可经 marketplace 分发 | 2026-10-22（运行验证） | `.omp/skills/verify-pstack-port/` 的 `doctor.py`、`probe_routing.py`；证据在其 `artifacts/`（本地，不入库） | [`ADAPTATION.md`](../pstack-omp/ADAPTATION.md) |
| [`pstack-dsh/`](../pstack-dsh/) | DeepSeek Harness | 0.15.29 @ `88d4751` | 🚧 进行中：只有骨架与调研，无 skill 正文 | 2026-10-24（仅调研） | 未开始；清单见 [`RESEARCH-prior-art.md`](../pstack-dsh/RESEARCH-prior-art.md) 第七节 | [`README.md`](../pstack-dsh/README.md) |
| [`pstack-kimi/`](../pstack-kimi/) | Kimi Code | 0.15.29 @ `88d4751` | ⏸ 暂停（2026-10-24） | 2026-10-24 | 无运行验证；迁移了基线并改写了 3 个入口，其余未完成 | [`README.md`](../pstack-kimi/README.md) 首段 |
| [`pstack-zh/`](../pstack-zh/) | 阅读用中文版（非插件） | 0.15.29 @ `88d4751` | ✅ 完成 | 未独立复核（按 README 自述记录于 2026-10-24） | 无脚本闸门；README 自述已对齐 0.15.29 | [`README.md`](../pstack-zh/README.md) |

状态取值只有四个：`⏸ 暂停`、`🚧 进行中`、`✅ 完成`、`🗑 归档`。不做"基本完成"这种中间态。

## 再生命令

上游 pin 与计数（改上游后重跑）：

```bash
cat UPSTREAM.json
git ls-files 'pstack-*/skills/*/SKILL.md' | wc -l
```

omp 的三段验证：

```bash
python .omp/skills/verify-pstack-port/scripts/doctor.py
python tools/fidelity/check_port.py --port pstack-omp --allow url
python tools/fidelity/outline_compare.py --upstream <上游根> --port pstack-omp --subdir skills --ignore bugbot-triage
```

dsh / kimi 目前没有可跑的验证命令；恢复或继续时先补 `verify/<platform>/`，再更新本表。

## 更新规则

1. 只记**最后确认过的结论**，不记计划。
2. 日期写实际跑命令的那天，不是写文档的那天。
3. 状态变化先改本表，再改相关文档里的指向。
4. 验证方式一栏必须能被人照着复现；做不到就不算已验证。