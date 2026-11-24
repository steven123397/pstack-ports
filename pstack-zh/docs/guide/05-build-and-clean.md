# 开发实现与清理 `diff`

几套开发 `playbook` 共享一条铁规：你把亲眼观察到的现象说出来，剩下的交给 `playbook` 去逼代理拿出证据。这一页讲清常见开发任务该怎么写 `prompt`，以及怎么把 `diff` 清得干干净净再送审。

## 把你已知的信息直接喂给开发 `playbook`

修 bug 的 `prompt`，先把症状说清并要求先复现：

```text
/poteto-mode 这个命令在重试后会吐出两条重复记录。先复现，再修复并验证。
```

做新功能的 `prompt`，把新行为和不能破坏的底线交代清楚：

```text
/poteto-mode 加一个 --json 参数。普通文本输出必须保持逐字节一致。两种格式都验证一下。
```

重构的 `prompt`，在动结构之前先把当前行为钉死：

```text
/poteto-mode 把解析逻辑收拢到一个模块里，零行为变更。先记下现在的输出，改完证明一模一样。
```

性能优化的 `prompt`，给实测数据，别给「感觉有点慢」：

```text
/poteto-mode 这份测试数据启动要花 1.8 秒。抓个 trace 定位实测瓶颈，修完把前后对比发我。
```

这几条会各自命中对应的 `playbook`（[Bug fix](../../skills/poteto-mode/playbooks/bug-fix.md)、[Feature](../../skills/poteto-mode/playbooks/feature.md)、[Refactoring](../../skills/poteto-mode/playbooks/refactoring.md)、[Perf issue](../../skills/poteto-mode/playbooks/perf-issue.md)），然后由 `playbook` 补齐你没手打出来的纪律：先复现再修、先定数据结构再写代码、先钉住行为再调结构、先抓 profile 再优化。

如果想围绕单个量化指标持续迭代优化，用 [Hillclimb playbook](../../skills/poteto-mode/playbooks/hillclimb.md)。给它指标名称、目标值和最少尝试轮数下限，它会用冻结好的压测 `harness` 每次只验证一个假设，确认有收益就提交保留，没收益全部回滚。

两套性能 `playbook` 都会对实测数字跑 [`/benchmark-checklist`](../../skills/benchmark-checklist/SKILL.md)。`Perf issue` 会核查基线和之后的每一次测数，`Hillclimb` 会在冻结 `harness` 之前先验一遍压测架子靠不靠谱。什么时候该自己手动调用它，见 [实跑验证与合入 PR](./06-verify-and-ship.md)。

有时候你只想先查清根因，不急着改代码。针对运行中的活症状（比如内存泄漏、空闲 CPU 空转、画面闪烁），[Runtime forensics playbook](../../skills/poteto-mode/playbooks/runtime-forensics.md) 会给活进程打点插桩。手里如果已经有抓好的性能产物，[Trace forensics playbook](../../skills/poteto-mode/playbooks/trace-forensics.md) 会直接读文件并把热点帧映射回源码行。这两套都只交诊断报告，不顺手改代码：

```text
/poteto-mode 这是启动慢抓出来的 cpuprofile。告诉我时间全耗在哪了，对应哪几行源码。先别修。
```

## 用 `/tdd` 先写必挂测试

如果一个 bug 有便宜好跑的本地单测路径，整条 `prompt` 甚至只要几个字：

```text
/tdd 实现修复
```

对话上下文已经齐了，这样就够。[`/tdd`](../../skills/tdd/SKILL.md) 会写出能按预期原因挂掉的最小测试，再写修复代码，然后重跑测试确认变绿。如果写测试非得搭一大套架子或堆一堆脆弱 mock，它会直说，转而改用最贴近真实场景的可执行命令验证。别为了硬凑单测放弃更有说服力的真实命令实跑。

## 按名字加载 TypeScript 规范

[`typescript-best-practices`](../../skills/typescript-best-practices/SKILL.md) 把类型系统原则落成了具体编码规矩：可辨识联合（discriminated unions）、边界用 `unknown`、分支穷尽检查、从 schema 派生类型。它不会自己悄悄加载，改 `.ts` 或 `.tsx` 文件时记得手动敲 `/typescript-best-practices`。

## 提交 commit 前先把脏东西洗掉

[Opening a PR playbook](../../skills/poteto-mode/playbooks/opening-a-pr.md) 在每次提交前都会对 `diff` 跑一遍 `/deslop`，而 `poteto-mode` 会拿 [`/unslop`](../../skills/unslop/SKILL.md) 过一遍 PR 描述和 commit 正文。`/deslop` 在 `cursor-team-kit` 插件里，不在 `pstack` 本包内。如果你没装那个插件，直接用大白话提同样的要求就行：删掉解说步骤的废话注释、没有依据的防御判断、没人调的兼容分支，以及跟本任务无关的顺手改动。

处理文字时，`/unslop` 可以指定目标并追加你自己的忌口：

```text
/unslop 清理一下 README 的改动，一个长破折号都别留
```

用顺了你会有自己的顺口令，像「过一遍 unslop，再压紧点」这种短话它完全听得懂。

## 用 `/no-comments` 把注释交出去单独过审

代码注释得单独过一轮，而且不能让写代码的那个代理自己审。作者总会护着自己写的注释，代理跟人一个德行。送审之前，换一双没包袱的新眼睛来看：

```text
/no-comments 检查这份 diff
```

[`/no-comments`](../../skills/no-comments/SKILL.md) 会派 [Comment Sicko](../../agents/comment-sicko.md) 上场。它是个只读注释审查员，手里的白名单极短：版权许可头、公共 API 文档注释、解释代码表达不出的约束链接，以及被外部依赖强迫产生且你改不了的怪异行为。白名单之外的一律砍掉。自家代码里的反直觉怪癖不在豁免之列，Comment Sicko 会把那条注释打成重构标记，由 `/no-comments` 从根因修掉。如果注释里写着「千万别删」这类约束，这个 `skill` 会提议把约束改写成类型、测试或 lint 规则。不管走哪条路，注释本身都得删。

这三个清理工具的分工记清楚：`/deslop` 清代码里的 `slop`，`/unslop` 清文案里的 `slop`，`/no-comments` 把注释交给没写过这段代码的人来砍。

**避坑提醒：** 清理环节不是锦上添花的可选项。满屏废话注释和冗余兜底代码的 `diff`，在评审人眼里就是半成品，而且多出来的代码往往就是下一个 bug 藏身的地方。觉得 `diff` 发胖了，提交前就喊一声 `deslop it`，别等 review 打回来再改。

下一篇：[实跑验证与合入 PR](./06-verify-and-ship.md)。
