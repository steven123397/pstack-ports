### Multi-phase or multi-PR plan

**计划归你把关，代码不归你写。计划是一份主理代理照着逐项打勾、操作者凭证据审计的清单。** 计划本身就是最终交付物，不要动手写业务代码。

1. 如果改动只涉及一两个文件且做法显而易见，直接跳过写计划，如实说明并停手。
2. 动笔之前先用原型把所有开放问题定死。每个疑问跑一遍 `playbooks/prototype.md`，留好分支名、SHA 和截图放进 Appendix A。只有实验定不了的产品或偏好选择才问操作者，并附上备选项（遵循 **never-block-on-the-human** `principle`）。
3. 派 `subagent_type: "poteto-agent"` 的子代理去摸底探索，并按 `Subagents` 一节明确指定模型、推理档位和速度（遵循 **guard-the-context-window** `principle`）。每个子代理只交回文件路径指针、仓库约定、测试命令和入口点，别往主对话塞大段原文。
4. 把下面这段骨架原样拷进计划文件，填满每一个占位符。除非操作者指定了路径，否则文件写在代理存储目录的 `docs/` 下。严格保留所有标题和子块的顺序。每个 PR 占一个大节，每个 PR 只做一件事并带齐自己的实跑证据（遵循 **sequence-verifiable-units** `principle`）。在 **How to read this** 里写明执行时走的 `playbook`：允许自动合入选 `playbooks/autopilot-full.md`，由操作者亲自合入选 `playbooks/autopilot-stack.md`，常驻大项目选 `playbooks/orchestrate.md`。
5. 全文按 `/technical-writing` 写完，再过一遍 `/unslop`。主体只用 Diátaxis 里的「操作指南（how-to）」一种文体，原理解释和参考资料全部放进附录。每个标题直说任务或发现。禁用长破折号，禁用句中冒号。
6. 运行 `node pstack/skills/poteto-mode/scripts/check-plan.mjs <plan.md>`，把脚本报出来的每一行问题全修干净（遵循 **encode-lessons-in-structure** `principle`）。
7. 交回计划。贴出计划文件路径和检查脚本的输出，然后停手。只有等操作者明确放行后，才按计划里指定的执行 `playbook` 开干。

**验证规则。** 光跑测试远远不算验证。一个 PR 只有当它的 unit、live 和 perf 三块勾选框全部打勾时才算通过验证（遵循 **prove-it-works** `principle`）。上面这两句英文原文（`Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.`）是固定校验句，每个验证子块都必须用它开篇。`Verify, live.` 必填：在 PR head 上按 **swarm** `skill` 跑 10 条实跑通道，使用 `swarm workers` 模型（默认 `claude-opus-5-5-high-fast`），经由对应的 control `skill` 驱动真实运行端。每条通道占一个勾选框，写清具体场景、保存的截图名和通过判定。其中一条固定为 **Regression lane against trunk.**，在主干和当前 head 上跑同一个核心场景；如果主干还没有这个功能，记录该事实，改为把关本 diff 新增的行为加上用户等待的最终状态，绝不凭空编造主干结果。性能门禁必须双侧对比，主干和 head 都要吐出同名指标；如果主干缺该功能，就隔离测本 diff 新增的工作量并定绝对预算，再加用户可见的端到端状态，别拿不同场景硬算倍率。性能块要写明指标、交替采样探针、先测出的主干基线，以及标明失败阈值的判定规则。凡是改变了用户交互的 PR 都受人工审批卡点约束，合入前操作者要在对话里看截图和录屏；没改交互的 PR 写 `**Review gate.** None. <PR id> is not review-gated.`，下面不列勾选框。

**Control `skill` 选型。** 按运行端挑：浏览器、Electron 和 Web UI 用 `cursor-team-kit` 的 `control-ui`；CLI 和 TUI 用 `cursor-team-kit` 的 `control-cli`；原生移动端用仓库里现有的模拟器驱动 `skill`。碰到两个端的 PR 两边都要开实跑通道。某个端没有 control `skill` 时，把它记为 Appendix C 里的风险，但 `Verify, live.` 块里仍要写清每条通道怎么驱动它。

> 注意：下面计划骨架里的英文标题、子块名与固定校验句会被 `scripts/check-plan.mjs` 做精确字符串校验，必须保留原文英文锚点；尖括号内的占位说明可按实际项目填写。

````markdown
# <项目名> plan

<10 行以内。改什么、给谁用、本项目守住的规则，以及按顺序排列的 PR 编号。>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA. The body is a how-to. The appendices explain and record.

The program runs `pstack/skills/poteto-mode/playbooks/<execution playbook>.md`. <谁来合入，以及哪些 PR 编号属于操作者自留项、走到 merge-ready 即停。>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State the protocol and this plan to the operator, then stop. Start execution only on the operator's explicit go.
- [ ] Read these from trunk at program start. Re-read them at every tick.
  - [ ] `git show origin/main:pstack/skills/poteto-mode/playbooks/<execution playbook>.md`
  - [ ] `git show origin/main:pstack/skills/swarm/SKILL.md`
  - [ ] `git show origin/main:<control skill path>`
  - [ ] `git show origin/main:pstack/skills/poteto-mode/playbooks/opening-a-pr.md`
  - [ ] `git show origin/main:pstack/skills/<本项目用到的其他叶子 skill>`
- [ ] On the operator's go, arm the audit tick as `/loop 1h` with the tick prompt below. Never leave the cadence to memory.
- [ ] Use this tick prompt, verbatim. "Re-read the execution playbook from trunk. Audit the operation against it and fix drift in this tick. Probe every active lane and judge progress by side effects only. Stand down a stuck lane and dispatch its replacement now. Then post a short status message to the operator in chat only when the audit found a tracked change that no earlier status message reported, such as a PR opened, a code-ready head, a round launched or closed, a verdict, a merge, a stuck agent and the action taken, a blocker added or cleared, or a decision only the operator can make. Name every such change and nothing else. Do not repeat a table, the merged list, or an unchanged blocker. If the audit found none, end the turn with no reply text. Either way, log this tick's row in your decision trail. The row names the items reported, or none."
- [ ] On the operator's hold or stand-down, send every owner a zero-writes order at once.

### Spawn owners

- [ ] Spawn one owner per PR with the full lifecycle the execution playbook names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when the execution playbook stacks.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id 或类别> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change an interaction. They wait for the operator's review in chat with screenshots and a video before merge.

### PR mechanics, for every PR

- [ ] Resolve the forge once. Default to `gh`; if `command -v origin` succeeds and Origin can resolve the repository, use `origin pr` for every PR operation. Record any fallback to `gh`. Never require `gt`.
- [ ] Open the PR ready, never draft, per **Opening a PR**. Use the run's built-in PR tool when it has one, else `origin pr create --status open --base <base-branch>` or `gh pr create --base <base-branch>` according to the resolved forge. A stack child targets its parent branch.
- [ ] Run the repo's lint and typecheck once before the PR-facing push. Push with hooks on.
- [ ] Run `/deslop` before each commit and `/no-comments` before review.
- [ ] Triage every Bugbot and security-reviewer comment per `../references/bugbot-triage.md`.
- [ ] Rebase onto current trunk before the code-ready report and babysit. Keep that merge base in fix rounds. Rebase again only at merge prep, on a `git merge-tree` conflict with trunk, on a CI failure that comes from a change on trunk, or when a known concurrent change to the same files lands.

### Verdict and merge, for every PR

- [ ] A full swarm runs once, at the code-ready head. Another full swarm runs only for new behavior, a redesign, or a large new diff. A rebase, a merge-conflict resolution, or a minor fix gets a single verifier at the new head, and a wording-only change gets none. Run each full swarm per `pstack/skills/swarm/SKILL.md`. One gates lane. The ten live lanes from the PR's **Verify, live** block. The perf lane from its **Verify, perf** block. Two or more audit lanes, each with its own focus, that read the diff and the receipts and distrust the PR body. The root audits the receipts in the merge-ready report before the verdict.
- [ ] Judge every finding by the execution playbook's blocking rule. The verdict is clean when none blocks. A failure on trunk behavior in a lane marked `Regression lane against trunk.` is recorded against trunk and does not block the PR. A new head gets a fresh verdict, except for results that stay valid under the patch-id rule in `playbooks/shipping.md`.
- [ ] <来自执行 playbook 的合入或交接规则，带上 playbooks/shipping.md 的 patch-id 规则。>

### Boot recipe, for every live lane

Each live lane runs on its own cloud VM at the PR head. Drive through `control-ui` or `control-cli` from `cursor-team-kit`.

- [ ] `git fetch origin <head-branch> && git checkout <head SHA>`.
- [ ] <启动后端与交互端，等待就绪。>
- [ ] <只通过 control skill 的命令输入操作，写明只读诊断方式。>
- [ ] Save every screenshot to `/tmp/swarm-<pr-id>/worker-<n>/<slug>.png` and return the paths with the report.

## <动词短语描述任务> (<PR id>)

**Depends on.** <PR id，或 None。>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <一项改动，点明具体符号和文件。>

**You see.**

- [ ] <一项可观察结果，写明确切日志行或界面状态。>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <测试文件及新增用例。> Run `<command>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on `<swarm workers model>` at the PR head, per the boot recipe.

- [ ] Lane 1. Regression lane against trunk. Run <核心回归场景> at trunk and head. If trunk lacks the feature, record that and gate <diff 新增行为加用户等待的终态>. Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 2. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 3. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 4. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 5. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 6. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 7. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 8. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 9. <场景。> Save `<slug>.png`. Pass when <判定条件>.
- [ ] Lane 10. <场景。> Save `<slug>.png`. Pass when <判定条件>.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. <在主干和 head 两侧测量的指标。若主干缺该功能，补上 diff 新增工作量与用户等待的端到端状态。>
- [ ] Probe. <在主干和 head 之间交替运行的命令或流程，两边都必须吐出指标。>
- [ ] Baseline. Record the trunk <基准值> first.
- [ ] Rule. <head 对照主干的判定规则及失败阈值。若两侧场景不同，给新增工作量与用户可见终态定绝对预算，不写无效倍率。>

**Review gate.** The operator reviews before merge.

- [ ] Copy lane <n> screenshots into `<media path>/<pr-id>-review-<slug>.png`.
- [ ] Record a 30 to 60 second video of the change on a lane VM. Save it as `<media path>/<pr-id>-review.mp4`.
- [ ] Post the screenshots and the video in chat. Stop at merge-ready. Wait for the operator's click.

**Merge.**

- [ ] Root's clean verdict at the exact head SHA.
- [ ] Bugbot triage done.
- [ ] Rebased onto current trunk after the verdict, patch-id unchanged.
- [ ] <由主理代理 squash 合入自己的 PR，或由根代理挂进叠栈交操作者自底向上合入。>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to the operator with the report the execution playbook names.

## Appendix A. Prototype evidence

<每个由原型定案的开放问题，附分支、SHA 和产物链接；仍未证实的问题一并列出。>

## Appendix B. Alternatives rejected

<权衡过的备选方案及落选理由。>

## Appendix C. Risks

<每项风险、它落进哪个 PR，以及主理代理需要盯紧什么。>

## Appendix D. Links and reading list

<动手前必读文档。哪些 PR 要跑 `pstack/skills/interrogate/SKILL.md`。按 `pstack/skills/show-me-your-work/SKILL.md` 记录的决策日志路径。>
````

**Reply：** 计划文件路径、各 PR 编号及依赖关系与需要人工审批的集合、原型证明了什么以及哪些尚未证实，还有检查脚本的输出。
