---
name: swarm
description: "并行扇出 N 个工人，等它们全部跑完收敛，再汇总交出一份统一报告。适用于 /swarm、「派一群工人并行跑」，或并行分片覆盖、赛马、多路并行测试线与批量探索。"
disable-model-invocation: true
---

# Swarm

## 开工起手式

派发任何工人前，先开一份待办清单，每个阶段占一项：

1. 定框（Frame）
2. 并行扇出（Fan out）
3. 汇总收敛（Aggregate）
4. 出报告（Report）

## Phase A：定框

1. 明确说出完成判定条件，以及这批工人最终要交回什么产物或报告。
2. 选定编排形态：按分片切块覆盖、让 N 个工人拿完全相同的 `brief` 赛马，或者两者混用。凡是涉及赛马或混合形态，开派前先声明胜出规则是 `first pass`、`rank all` 还是 `best-of`。
3. 从 `~/.cursor/rules/pstack-models.mdc` 的 `swarm workers` 行挑选工人模型。如果规则文件或该行缺失，默认用 `claude-opus-5-5-high-fast`。配成 `auto` 或 `inherit-parent` 时，省略 `model` 参数让工人沿用父会话模型。如果 `Task` 工具拒绝了某个 `slug`，回退到默认值并说明；如果连默认值也被拒绝，从报错信息里选同一家族最接近的合法 `slug`。如果是多模型赛马，提前写明每一路跑哪个模型。按 **poteto-mode** `skill` 的 Subagents 章节，为每个子代理选定匹配的推理档位与 fast/standard 速度。
4. 需要写文件的工人，每人分配独占的可写输出位置。如果工人负责验证或压测特定 commit，每份 `brief` 都必须点名确切的 SHA；涉及性能测量的 `brief` 还要写清测量方法（采样次数、单次样本定义、交替顺序），并要求工人在结果里把 SHA 和方法原样记下来。

## Phase B：并行扇出

在单条消息里一次性并发派发全部 N 个工人，设置 `subagent_type: generalPurpose`、`environment: "cloud"`、`run_in_background: true`，以及第 3 步选定的模型（为 `auto` 或 `inherit-parent` 时留空不传）。只有在工人必须访问用户本机资源时，才改用 `environment: "local"`。

如果工人必须从某个已推送的非默认分支起步，传入 `cloud_base_branch`。

每一份 `brief` 都要自成一体、不依赖外部上下文，包含目标、范围、确切的分片或赛马分支、验证方式，以及汇报格式。汇报状态统一用 `PASS`、`ISSUES` 或 `BLOCKED`，并附证据。能实证缺陷的工人必须报 `ISSUES`，而且要把自己能证明的所有问题全列出来，绝不只报第一个。

如果某个工人掉线或无结果返回，用剩下的 N-1 份继续推进，并记下缺席情况。

## Phase C：汇总收敛

读取全部终态结果。如果某份结果没按 `brief` 要求记录确切 SHA 和测量方法，直接丢弃该结果，并重派该工人一次。第二次依然漏记，就记为一个覆盖缺口（gap），缺口绝不算通过。对于覆盖类任务，每个必测分片都必须有有效结果。对于赛马类任务，严格执行开头声明的胜出规则（`first pass`、`rank all` 或 `best-of`）。绝不要把工人的原始大段输出直接粘贴进报告。

## Phase D：出报告

在对话里交回一份汇总整理后的完整报告，包含结果总表、逐条问题一句话摘要、覆盖缺口或掉线记录，以及用到了赛马时的胜出规则。
