### Opening a PR

附在其余所有 `playbook` 末尾的统一收尾动作。

**Worktree。** 从 `main` 拉出的独立 git `worktree` 里开展工作，子代理会继承它。在同一个分支上多次调 `Task` 时，要么各自单开 `worktree`，要么两次之间先 `git fetch && git reset --hard origin/<branch>`。如果当前分支脏了且混着无关改动，先把目标改动打 patch 抽出来，新开干净 `worktree` 再应用。要是 `worktree` 彻底搞乱了，从 `main` 重置一份最简重做。

**Commits。** 干活时小步勤提交。开 PR 前先 rebase 成小步、有序的 commit，每个 commit 都像一个独立可合入的小 PR，按顺序讲清改动脉络。如果某次修补本来就属于刚打完的那个 commit，直接 amend；能拆开成独立逻辑的就打新 commit。commit 正文不要把标题换句话再复述一遍。

**PR 清理与文案。** 提交前对 `diff` 跑 `cursor-team-kit` 里的 `/deslop`，送审前跑 `/no-comments`。所有 PR 标题、描述和 commit 正文都用 `/technical-writing` 写（套用除 Diátaxis 外的全部层级，并落实 STE 词汇纪律：同一动作固定一个词、保留清晰主语指代、能用直白动词别用绕口名词化），最后过一遍 `/unslop`。

**标题。** 采用 Conventional Commits 格式 `type(scope): subject`，末尾不加句号。`type` 如 `feat`、`fix`、`docs`、`refactor`、`test`、`chore` 或 `perf`；`scope` 写模块范围如 `pstack` 或 `poteto-mode`；`subject` 简短有力，用祈使语气，如果改动集中在某个核心符号就直接点名（例如 `fix(pstack): retarget opening-a-pr babysit trigger`）。

**描述正文。** PR 正文是给手里已经拿着 `diff` 的评审人看的一分钟简报，不是实验流水账。交代清楚为什么改、刻意没动什么、可能影响什么，以及怎么证明它真的能跑通。用简短直白的句子，少堆代码标识符，别写密不透风的大段文字墙。正文最终会变成 squash commit 消息，因此控制在 40 行以内。统一用 `##` 二级标题（别用加粗段首代替），按下面顺序排列，没内容可写的小节直接省略：

- `## Why`：要解决的问题与核心思路，1–3 句短话。不写 SHA、变基族谱或「基于 main」这类废话开场。
- `## What changed`：1–3 条简短要点。只有真实承载改动的符号或路径才点名；涉及重命名或改指向时把新旧两边都写清楚。
- `## Scope`：必写。1–3 条短句，说清本次涵盖什么、刻意留到后面的又是什么（后续单、已知缺口）。不写符号列表、路径清单或逐文件流水账。
- `## Tradeoffs`：只写评审人很可能会追问的被否决方案。如果本来就没有真实分叉，直接略过。
- `## Blast Radius`：1–2 句话说清波及到谁或哪些模块，以及为什么安全或存在何种风险。如果 `main` 当前本来就是红的，写明放着不管的代价。
- `## Verification`：1–3 条要点，每条写明真实运行路径与结果。性能类改动只给一个带单位的核心主指标（`before → after`），其余细节放 `arena` 或 `swarm` 目录链接。不把采样方法论、各路工人流水账或大张指标表贴进正文。

上述小节之后，如果录屏或截图能证明结论就直接附上。完整 SHA、`swarm`/`arena` 各通道记录、长篇纠偏分析、逐文件清单以及「CLEAN」大段评审报告，全都放进外部链接产物，不塞正文。

**代码托管平台（Forge）。** 第一次操作 PR 之前先判定当前平台，并在后续创建、编辑、查看、监听和合并全程保持一致。默认用 GitHub CLI（`gh`）。如果 `command -v origin` 成功且 Origin 能解析当前仓库，优先用 `origin pr ...`；如果本机没有 Origin 或无法解析仓库，留在 `gh` 并记录回退情况。不要依赖 Graphite（`gt`）。

**内置 PR 工具。** 如果当前环境提供了内置 PR 工具，创建、编辑、改 base 分支和标记 ready 一律走它，别绕过去调 CLI，否则内置工具会丢掉追踪状态。只有内置工具不支持的操作，或者当前环境根本没有内置 PR 工具时，才走上面判定好的托管平台 CLI。

**体量与叠栈。** 宁可开五个窄而聚焦的小 PR，也不要塞成一个大 PR。PR 栈本质上是一条 base 分支链：最底部的根 PR 指向主干分支，每个子分支 rebase 到父分支的精确最新 commit 并把 PR base 设成父分支。父 PR 一旦合入，按 `playbooks/shipping.md` 第 4 步把子 PR 移到主干上。没有内置 PR 工具时，按已判定的平台用 `origin pr create --status open --base <parent-branch>` 或 `gh pr create --base <parent-branch>` 创建子 PR，用 `origin pr edit <pr> --base <parent-branch>` 或 `gh pr edit <pr> --base <parent-branch>` 调整 base。只有彼此独立的工作才直接从主干拉分支。开始大规模叠栈前先基于主干 rebase 一次。

**就绪状态。** 每个 PR 开出来都直接是 ready 状态，绝不开成 draft。有些内置 PR 工具默认开成 draft，调用时必须显式传 `draft: false`。用 Origin 时传 `--status open`；用 `gh` 时不传 `--draft`。如果开完发现还是 draft，立刻通过 PR 工具标成 ready，或按平台执行 `origin pr ready <number>` / `gh pr ready <number>`。每次对外汇报 PR 状态前，先跑 `origin pr view <number>` 或 `gh pr view <number>` 核实。

**Babysit 边界。** 刚开出 PR 不会自动启动 `Babysit`。贴完链接直接继续干活，先把当前阶段或整叠 PR 建完。等整叠都就绪且用户明确要求时，再单独跑一轮 `Babysit`。每开一个 PR 就停下来盯盘会拖垮开发节奏，还会把 CI 浪费在后续推送马上就会刷掉的 commit 上。遇到偏离初衷的评审意见要敢于据理反驳。

子代理开 PR 时要跑完 `/deslop` 和 `/no-comments` 并贴出链接，然后直接向父级交卷，不要擅自进入盯盘循环，除非它是 `Autopilot-full` 或 `Autopilot-stack` 的主理代理（`owner`）。这类主理代理的 `brief` 本身就指派了盯盘循环，等同于 `playbooks/babysit.md` 等待的触发指令；它在报完代码就绪后直接起循环，直到汇报已就绪可合入，不受此处和 `playbooks/babysit.md` 中「等整叠建完再盯盘」的限制。
