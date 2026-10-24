# 验证资产

移植要回答两个不同的问题：**保真**（改写有没有丢规则）和 **可跑**（装进目标 harness 后行为对不对）。前者靠 `tools/fidelity` 的只读脚本，后者靠平台侧的运行验证；本文件是后者的索引。

## 通用闸门（所有平台）

```bash
python tools/fidelity/check_port.py --port pstack-<platform> --allow url
python tools/fidelity/outline_compare.py --upstream <上游根> --port pstack-<platform> --subdir skills
```

`problems 0` 与 `failures 0` 是硬条件，提交前必跑。用法与通过标准见 [`tools/fidelity/README.md`](../tools/fidelity/README.md)。

## 平台运行验证

| 平台 | 位置 | 形态 | 说明 |
| --- | --- | --- | --- |
| omp | [`.omp/skills/verify-pstack-port/`](../.omp/skills/verify-pstack-port/SKILL.md) | repo-local omp skill：`engine` 入口 + `scripts/doctor.py` + `scripts/probe_routing.py` + `features/` | 覆盖安装、skill 解析与调用、四个 agent 的模型落点。`artifacts/` 被 `.gitignore` 排除，证据本地保留 |
| dsh | 待建 `verify/dsh/` | 按 [`pstack-dsh/RESEARCH-prior-art.md`](../pstack-dsh/RESEARCH-prior-art.md) 第七节清单 | 至少覆盖：`agentOptions` 是否接受 model/effort、preset `toolFilter` 是否 per-child 生效、`ctx.commands` 的 `/name` 注入、bundle `customSkillDirs` 加载、`dsh plugin add github:` 的 bundles 坑 |
| kimi | 无 | — | 适配已暂停，未做运行验证 |

## 为什么 omp 的验证不放在 `verify/` 下

omp 只从 `.omp/skills/<name>/SKILL.md` 发现项目级 skill，搬走就加载不到。所以 `verify/` 只做索引，真实资产留在平台约定路径；dsh 若也需要项目级 skill，同理放 `.dsh/skills/` 并在上表登记。

## 证据策略

- 入库的是**可复现的命令与通过标准**；原始证据（`artifacts/`）不入库，避免体积与会话隐私，但清理时不要删除。
- 一次验证记三样：命令、退出码、stdout。模型路由类验证还要记 `resolvedModel` 与 `modelRole` 配置的对照——父会话自己的模型不能作为证据。
- 失败的迭代与通过的迭代保留同样证据，结论写进 [`docs/status.md`](../docs/status.md) 的"最后确认"与"验证方式"两列。