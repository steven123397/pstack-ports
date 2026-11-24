# pstack 中文术语表与行文规范

本规范统管阶段一 `pstack-zh/`（忠于上游英文原版 `0.15.48` 的高质量中文版）与阶段二 `pstack-omp/`（基于中文底座的 `omp` 中文适配插件）。

核心原则是**不为了"全中文"而硬造汉语概念**。编码代理领域通用的英文词，以及插件里全部具体的 `skill`、`playbook`、`principle` 名称，一律保留英文原名；其余逻辑、动作、条件与工程判断，则全部译成中国资深工程师日常说话的直白汉语，彻底去掉英文语序和翻译腔。

## 一、四类处理规则

1. **专名与行话保留英文**：插件专有结构词、coding agent 通用行话、所有具体 `skill` / `playbook` / `principle` 的原名、命令入口（`/poteto-mode`）、代码块、路径、模型 `slug`（如 `claude-opus-5-5-xhigh-fast`）和状态枚举（`PASS`、`ISSUES`、`BLOCKED`、`READY`、`WAITING`、`COMPLETE`），一律保留英文。
2. **动作与工程逻辑意译**：把英文长句、被动语态和名词堆砌，彻底拆成中文日常工程口吻的动宾短句。
3. **一词多义按语境说人话**：碰到 `frontier`、`lane`、`gate`、`surface` 这类多义词，不强行定死一个中文或英文单词，直接按当前上下文写出它实际指代的东西。
4. **只在一处改规范**：要调整某个词的译法，先改本表，再全库同步。

## 二、保留英文的高频词（不硬译）

以下词在 coding agent 语境里已经约定俗成，硬翻成中文反而更抽象：

| 英文 | 保留形式与中文句子用法 |
| --- | --- |
| `skill` | 保留 `skill`，例如「每条 principle 对应一个独立的 `skill` 文件」 |
| `playbook` | 保留 `playbook`，例如「`poteto-mode` 内置 22 个 `playbook`」 |
| `principle` | 保留 `principle`，指代那 24 条工程原则；泛指时可写「原则」 |
| `slop` / `unslop` / `deslop` | 保留 `slop`，例如「别写 `slop` 代码」「输出过一遍 `unslop`」；初见时可顺带说明它指 AI 生成的敷衍代码或空话 |
| `brief` | 保留 `brief`，例如「给子代理的 `brief` 里写明验收标准」 |
| `harness` | 保留 `harness`（指 Cursor / omp 这类 Agent 运行框架，或压测/验证驱动架子；必要时写「测试 `harness`」区分） |
| `worktree` | 保留 `worktree`（初见可附注「Git worktree」） |
| `prompt` | 保留 `prompt`（交互引导文案中也可用「提示词」，不强制二选一，保持同段统一即可） |
| `eval` | 保留 `eval`，例如「跑一轮盲测 `eval`」 |
| `slug` | 保留 `slug`，指模型标识串（如 `claude-opus-5-5-xhigh-fast`） |
| `PR` / `CI` / `MCP` / `diff` / `commit` / `rebase` / `squash` / `merge` / `flake` | 保留常见 Git 与工程缩写，按国内程序员正常说话方式混用 |
| `Feature Map` / `Custom Mode` / `always-applied rule` | 保留专名，初见时用大白话带一句中文解释 |

## 三、一词多义·按语境写实

遇到下面这些词，根据原文所处位置直接写清楚具体所指：

| 英文 | 语境 A 与写法 | 语境 B 与写法 |
| --- | --- | --- |
| `frontier` | `frontier model` → **前沿模型** | `merge frontier`（`Babysit`）→ **合入前沿（当前最底端待合的 PR）** |
| `lane` | `swarm` 的 `gauntlet lanes` → **多路并行测试线** | `Shipping` / CI 中的 `lane` → **单条检查通道 / 检查项** |
| `gate` | 需人拍板的 `review gate` → **人工审批卡点** | 自动阻断的 `regression gate` → **回归门禁** |
| `surface` | `UI / IDE / CLI surface` → **真实运行端 / 交互界面** | `API surface` → **对外接口面** |
| `rule` | `.cursor/rules/*.mdc` → **规则文件** | `statechart` / 不变量里的 `rule` → **业务约束 / 规则** |
| `drive` | `drive the app` → **实操运行应用（模拟用户点一遍）** | `Babysit` 的模式值 `drive` → 保留枚举 `drive`（全程护航模式） |

## 四、通用工程与流程词汇推荐写法

这些词没有必要留英文，用直白的中文工程表达最清楚：

### 1. 角色与协作

| 英文 | 推荐中文写法 | 说明 |
| --- | --- | --- |
| `subagent` | **子代理** | 统称，不混用「子智能体」「分身」 |
| `cloud agent` | **云端代理** | 在远端虚拟机或独立沙箱里运行并推分支的代理 |
| `coordinator` | **总控会话**（或「协调者」） | 负责拆解、派发与验收，自己不直接写代码的主会话 |
| `owner` | **负责人 / 主理代理** | 对某一个 PR 或整段任务从头负责到底的代理 |
| `verifier` | **独立验证代理** | 专门负责验证改动效果的全新子代理（严禁由写代码者兼任） |
| `runner` | **参赛代理** | `arena` 中各自独立出方案的并行代理 |
| `panel` / `seat` | **多模型评审团** / **席位** | 多模型协同中的评审阵容与单个模型位 |
| `cross-judge` | **跨家族裁判（`cross-judge`）** | 必须来自与主会话不同模型家族的只读裁判 |
| `adversary` | **对抗评审代理** | `interrogate` 中专门试图把改动跑崩、找真实缺陷的一方 |
| `operator` / `user` | **操作者** / **你（用户）** | 自动化批处理拍板用「操作者」，日常引导用「你」或「用户」 |
| `consumer` / `maintainer` | **使用方** / **维护者** | 回复规范要求同时说明对这两类人的影响 |
| `leaf skill` | **叶子 `skill`** | `principle-*` 这类最末端的单页 `skill` |
| `steer` | **纠偏 / 掌舵** | 通过点名 `principle` 在中途拉正代理方向 |

### 2. 实验、评审与运行控制

| 英文 | 推荐中文写法 | 说明 |
| --- | --- | --- |
| `throughput checkpoint` | **4 项并行拆解检查点**（可附 `throughput checkpoint`） | `Feature` 第 3 步列在 todo 里的 4 个并行判断项 |
| `bakeoff` | **多方案同题比拼** | 并跑几个方案再对比选优 |
| `pick a base` | **选定基底方案** | 从候选方案里挑出最稳的一个作为底座 |
| `graft` | **手工吸取合并（嫁接）** | 把落选方案里最值得留下的点手工融合进基底，不机械粘贴 |
| `rubric` | **评分标准** | `arena` 用来逐项打分的 3–6 条具体准则 |
| `verdict` | **判定结论** | 带明确状态的终审结论，如「通过」「未通过」「就绪」 |
| `finding` | **查出的问题** | 对抗评审或审查中拿实证跑出来的具体问题条目 |
| `dropped` | **已剔除项** | 未能通过复现验证而被丢弃的条目 |
| `nitpick` | **吹毛求疵 / 琐碎挑刺** | 不影响正确性与设计的细枝末节挑剔 |
| `contested design` | **有争议的设计** | 存在明显分歧、改动代价高、需要对抗验证的设计 |
| `throwaway sketch` | **用完即弃的草样原型** | 只用来验证疑问或比选方案，绝不当作正式代码留用 |
| `decision trail` / `decision log` | **决策日志**（`decisions.tsv`） | 供事后审计每一步取舍的 TSV 记录 |
| `overnight contract` | **过夜 / 无人值守交接约定** | 离开前写清目标、完成判定、权限和退出条件的约定 |
| `escape hatch` | **止损退出条件** | 遇到死胡同时允许停下并写明原因，防止瞎折腾一晚上 |
| `stop the line` | **发现问题立即叫停** | 任何环节发现不达标就停下，不把隐患传到下一棒 |
| `cold-start agent` | **冷启动代理** | 没有任何前序上下文、全靠交接说明接手的新代理 |
| `consolidated scope` | **汇总整理后的完整任务范围** | 重派新代理时，把初始 `brief`、后续新增指令与前任结果并在一起 |
| `interrupt-chained resume` | **被打断后在原代理上直接续接** | 容易静默丢失中途指令的做法，应默认开新子代理替换 |
| `session override` | **会话级覆写指令** | 如「别停」「我要睡了」，授权跳过可撤回工作的确认直接推进 |

### 3. Git、PR 栈与合入流

| 英文 | 推荐中文写法 | 说明 |
| --- | --- | --- |
| `stack` / `stacked PRs` | **PR 栈 / 叠栈 PR** | 按依赖关系逐层叠加的一串 PR |
| `trunk` | **主干分支** | 目标主分支（如 `main`） |
| `land` | **合入主干** | 把已验证通过的 PR 正式合进目标分支 |
| `upstack` | **上层 PR** | 栈中位于当前待合 PR 之上的后续 PR |
| `merge-ready` | **已就绪可合入** | 冲突、评论、CI 全清零，只等点 merge |
| `contiguous verified run` | **从栈底起连续验证通过的一段 PR** | 只要中间断了一个没验过，后面的再绿也不能先合 |
| `ceiling` | **这段可合入序列的上限 PR** | 连续验证通过序列最顶端的那一个 PR |
| `forge` | **代码托管平台** | 指 GitHub 或 Origin |
| `triage` | **逐条甄别定性** | 逐条核对报错或评审评论，决定修复、驳回还是询问 |
| `drift sweep` | **偏移扫尾检查** | 变基时顺带清查主干新合代码里是否又新增了旧接口调用 |
| `stale base` | **base 分支过期** | 底层依赖分支落后主干导致的问题 |

### 4. 代码、类型与验证

| 英文 | 推荐中文写法 | 说明 |
| --- | --- | --- |
| `brand semantic primitives` | **用 Branded Types 区分语义不同的基础类型** | 例如让 `UserId` 和 `OrderId` 底层都是字符串但在编译期不可混用（严禁译作「打上品牌」） |
| `make illegal states unrepresentable` | **让非法状态在类型上无法构造** | 靠类型建模在编译期堵死不可能的组合 |
| `exhaust variants` | **穷尽所有分支变体** | 让编译器检查联合类型/枚举是否处理完每种情况 |
| `parse external data at boundaries` | **在系统边界解析外部数据** | 在入口把非结构化输入转成强类型模型，内部只信类型 |
| `one-caller wrapper` | **只有一个调用方的多余包装层** | 毫无必要多包一层的函数或类，直接拆平 |
| `bolting on` | **硬往上打补丁拼装** | 不调整根基假设，直接把新需求生硬外挂上去 |
| `dead weight` | **死代码与冗余包袱** | 没人用的代码、重复校验、失效桩引用 |
| `proxy`（验证语境） | **表面替代指标** | 看似相关但不能真证明行为对的指标（如「能编译」「单测全绿」） |
| `invariant` | **不变量** | 在所有合法状态下必须始终成立的系统条件 |
| `counterexample` | **反例路径** | 模型检测器给出的打破规则的最短状态轨迹 |
| `model checker` | **模型检测器** | 例如校验 TLA+ 规约的 TLC |
| `baseline` | **基线** | 改动前冻结的基准数据或对比版本 |
| `limiter` | **瓶颈限制因素** | 实测性能上不去时真正卡住上限的物理或系统原因 |
| `median` / `range` | **中位数 / 波动区间** | 多次交替采样跑分时必填的数据指标 |
| `inconclusive` | **结论未定** | 条件不满足或跑不出来时诚实标出，绝不硬凑通过 |

## 五、24 个 `principle`、22 个 `playbook` 与 35 个 `skill`（全部保留英文原名）

全库正文中出现以下名字时，**一律保留英文原名**。下表中的中文只用于帮你快速记住「它管什么、什么时候用」，不作为替换原文名字的新造词。

### 1. 24 个 `principle`（`principle-<slug>`）

| 分组 | 英文原名（正文保留） | 一句话中文释义（做什么 / 何时用） |
| --- | --- | --- |
| Core | **Laziness Protocol** | 优先删代码而不是加代码，做能解决问题的最小改动 |
| Core | **Foundational Thinking** | 写逻辑前先把核心类型、数据结构、搭架与功能顺序、并发共享状态想清楚 |
| Core | **Redesign from First Principles** | 融入新需求时，按「第一天就有这个需求」的思路重构，不生硬打补丁 |
| Core | **Attack the Premise** | 同一个前提下的两种修法都在同一关失败时，先把那个前提写出来直接验证 |
| Core | **Subtract Before You Add** | 动手重构或新增前，先把死代码、冗余校验等包袱减掉 |
| Core | **Minimize Reader Load** | 删掉单调用方套壳、收缩可变状态范围，减少读代码人的脑力负担 |
| Core | **Outcome-Oriented Execution** | 计划好的重写和迁移直接向目标架构收敛，别为过渡态保留注定要扔的兼容代码 |
| Core | **Experience First** | 产品与范围取舍时，宁可少做几个但做好，不要为了好写牺牲使用体验 |
| Core | **Exhaust the Design Space** | 没有先例的新交互或架构决策，先做 2–3 个互相竞争的原型比一比再定 |
| Core | **Build the Lever** | 非琐碎的工作别光靠手搓，造出能自动化完成或可复跑证明的工具脚本 |
| Architecture | **Model the Domain** | 有状态或分支散落多处时，用状态机、类型模型或表结构集中表达领域逻辑 |
| Architecture | **Boundary Discipline** | 校验和兜底集中在 CLI/配置/网络等系统边界，内部保持纯函数和类型可信 |
| Architecture | **Type System Discipline** | 让非法状态无法构造、区分 Branded Types、边界解析、穷尽分支、从权威 schema 派生类型 |
| Architecture | **Make Operations Idempotent** | 声明命令、生命周期步骤或循环必须幂等，崩溃重试都能收敛到同一终态 |
| Architecture | **Migrate Callers Then Delete Legacy APIs** | 推新内部接口时，在同一轮里迁完所有调用方并立即删掉旧接口 |
| Architecture | **Separate Before Serializing Shared State** | 多方并发可能写同一文件或分支时，先拆开消除共享；真是不变量才加串行化 |
| Verification | **Prove It Works** | 交付前必须对着真实产物实跑验证，别拿「能编译」或口头汇报交差 |
| Verification | **Fix Root Causes** | 从报错症状一直追到系统第一次走偏的地方去修，别只加表面防御 |
| Verification | **Sequence Work into Verifiable Units** | 多步改造拆成以检查收尾的小单元，每步验证完再走下一步，提交顺序自证清白 |
| Verification | **Test Behavior, Not Implementation** | 测试只断言外部可观察行为，内部重构时不该随便挂掉 |
| Verification | **Explain the Number** | 汇报或相信任何实测数字前，查明瓶颈所在，排除测错对象的可能 |
| Delegation | **Guard the Context Window** | 长输出、大文件、批量读代码和扇出探索全丢给子代理，主对话只留摘要 |
| Delegation | **Never Block on the Human** | 可撤回的活别老问「我能不能做 X」，先做出来把结果给人看，留给人纠偏 |
| Meta | **Encode Lessons in Structure** | 同一句话提醒代理超过两次，就把它写成 lint、元信息校验或脚本，别再写纯文本 |

### 2. 22 个 `playbook`（`skills/poteto-mode/playbooks/`）

| 文件名 | 英文原名（正文保留） | 中文定位说明 |
| --- | --- | --- |
| `investigation.md` | **Investigation** | 只读调研：只查证带出处回答，不改代码 |
| `bug-fix.md` | **Bug fix** | 修缺陷：先复现、追根因、再修复并拿运行时证据 |
| `perf-issue.md` | **Perf issue** | 修性能：先抓基准 profile 再定位优化，用实测对比交差 |
| `hillclimb.md` | **Hillclimb** | 爬坡迭代：围绕单一量化指标持续提假设、单步实测、有收益才保留 |
| `runtime-forensics.md` | **Runtime forensics** | 运行时取证：给活进程打点抓内存泄漏、空转 CPU 或卡顿根因 |
| `trace-forensics.md` | **Trace forensics** | 产物取证：分析抓好的 cpuprofile、trace、spindump 或 heap snapshot |
| `feature.md` | **Feature** | 做新功能：先定数据结构，列 4 项检查点，委派实现并实跑验收 |
| `refactoring.md` | **Refactoring** | 重构：只改代码结构不改外部行为 |
| `prototype.md` | **Prototype** | 原型验证：用用完即弃的草样低成本解决设计分歧或实证疑问 |
| `visual-parity.md` | **Visual parity** | 视觉对齐：对照冻结基线逐像素 diff 校准 UI |
| `authoring-a-skill.md` | **Authoring or modifying a skill** | 编写或修改 `SKILL.md` 的标准流程 |
| `eval.md` | **Eval** | 盲测评估：`skill` 或 `prompt` 改动后盲跑对比效果 |
| `babysit.md` | **Babysit** | 盯盘护航 PR：按顺序清冲突、评论和 CI 直到可合入（不代点 merge） |
| `shipping.md` | **Shipping** | 栈式合入：独立验证 PR 栈后从底部起逐个合入连续通过的序列 |
| `autonomous-run.md` | **Autonomous run** | 无人值守单任务循环：盯着完成判定一直跑完 |
| `autopilot-full.md` | **Autopilot-full** | 全自动队列托管：独立 PR 队列从开发、群体复核到自动合入一条龙 |
| `autopilot-stack.md` | **Autopilot-stack** | 全自动叠栈（只建不合）：造完并验完叠栈 PR，留给人拍板合入 |
| `session-pickup.md` | **Session pickup** | 断点续接：从记录、云端链接或远端分支接手前任中断的活 |
| `pause-safely.md` | **Pause safely** | 安全挂起：保存现场 checkpoint 与交接说明，方便后续冷启动恢复 |
| `multi-phase-plan.md` | **Multi-phase or multi-PR plan** | 跨阶段或跨多个 PR 的拆解计划（只交计划文档不直接写业务代码） |
| `worktree-cleanup.md` | **Worktree and simulator cleanup** | 安全审计并清理已合或废弃的 `worktree` 与过期模拟器，释放磁盘 |
| `opening-a-pr.md` | **Opening a PR** | 收尾开 PR：整理小步有序 commit，写清背景与验证证据 |

### 3. 其余 35 个 `skill` 与 2 个子代理（全部保留英文原名）

| 名称 | 一句话中文说明 | 名称 | 一句话中文说明 |
| --- | --- | --- | --- |
| `poteto-mode` | 总控入口，按任务匹配 `playbook` 并统筹子代理 | `benchmark-checklist` | 7 项性能跑分核查清单，防假提速 |
| `poteto-help` | 新手选型向导，答疑并给出可直接发送的 `prompt` | `no-comments` | 审前清理废注释，调用 `comment-sicko` |
| `setup-pstack` | 检测可用模型并配置各角色路由与推理预算 | `typescript-best-practices` | TypeScript 类型系统实操规范 |
| `in-your-own-words` | 开工前先用大白话复述目标与要解决的问题 | `figure-it-out` | 当内置 `playbook` 都不贴合时，现搭一套可审计流程 |
| `sharpen` | 把 `prompt` 改得更深入（不膨大），补齐原型验证要求 | `show-me-your-work` | 记录可审计的 `decisions.tsv` 决策日志 |
| `reframe` | 说不清需求时拆解歧义、教专业术语与邻近领域借词并重写描述 | `create-verification-skill` | 为当前项目自动生成可实跑应用的本地验证 `skill` |
| `how` | 派只读子代理讲透某块代码的架构与运行流 | `maintain-verification-skill` | 定期核对并校准项目本地验证 `skill` 与 `Feature Map` |
| `why` | 考据 commit 和 PR 历史，查清当初为什么这么写 | `create-formal-verification-skill` | 对并发/状态机等难测代码生成形式化验证 `skill` |
| `recall` | 跨聊天历史、现场与问题单重建近期上下文 | `maintain-formal-verification-skill` | 代码改了之后校准形式化模型与不变量检查 |
| `ketchup` | 用人话和简图同步最新进展，列出待拍板项 | `statechart` | 跑 TLA+ 模型检测并画成 Mermaid 状态图与最短 bug 路径 |
| `ketchup-video` | 把 `/ketchup` 内容做成带字幕的短幻灯片视频 | `unslop` | 删掉文本里的 AI 套话和废话 |
| `blast-radius` | 查出改动会影响哪些远端调用，并用实跑代码证明安全 | `bro` | 用毫无术语的大白话重说一遍上一条消息 |
| `architect` | 跨函数边界写代码前梳理受影响系统并对比方案形状，争议大时转交 `arena` | `technical-writing` | 四层技术文档写作标准（Diátaxis + Google + STE + 全球英语） |
| `arena` | 并行跑 N 个方案，选出基底并手工吸收各家优点 | `reflect` | 直接复盘当前对话 transcript，把教训沉淀为对已有 `skill` 的修改 |
| `swarm` | 并行撒出 N 个工人跑分片检查或赛马，汇总成一张报告 | `correct` | 挖掘历史反复犯的同类错误，从架构/类型/lint 层根治 |
| `interrogate` | 多模型对抗挑刺，只有跑出实证的缺陷才算有效 `finding` | `automate-me` | 从你的近期工作记录里提炼专属 `-mode` 个人 `skill` |
| `tdd` | 修有便宜本地单测的 bug 时，先写失败测试再修代码 | `make-bot-ui` | 搭一个通过 webhook 唤醒 Grok Bot 的控制面板 |
| `teach` | 串联 `how` 和 `why` 并配小图，把模块彻底讲懂 | — | — |

内置子代理名保留：`poteto-agent`、`comment-sicko`。

## 六、中文行文与去 AI 腔契约（中文版 `unslop`）

写全部文档、`skill` 正文和回复模版时，遵守以下硬规则：

1. **像资深工程师和同事直接交代任务**。多用短句、主动语态、明确主语。别写「我们可以看到」「值得注意的是」「总而言之」「基于以上考量」「对其进行……处理」。
2. **禁用长破折号（`——`）和句子中间的冒号**。需要断句就直接句号收尾，列表前的冒号除外。
3. **禁用空泛的互联网黑话与伪术语**。不用「赋能」「抓手」「闭环」「沉淀（非具体动作）」「对齐颗粒度」。把抽象词换成具体动作和对象。
4. **每一个判断同句带上依据或定性标签**。写清楚是「实测」「推断」还是「猜测」，不写没根据的肯定词。
5. **用中文开发者真会说的话改写触发条件**。在 `description` 与触发清单里，优先写自然中文口语，同时适当保留高频英文触发词（如 `babysit`、`interrogate`、`arena`）以便中英混用场景也能命中。

### 常见英文触发口令 → 地道中文参考

| 英文口令 | 中文自然表达 | 英文口令 | 中文自然表达 |
| --- | --- | --- | --- |
| `are we sure?` | 「我们确定吗？」「这靠谱吗？」 | `repro first` | 「先复现再动手」 |
| `don't change any code yet` | 「先别改代码」 | `let me review before proceeding` | 「继续前先让我看一眼」 |
| `going to bed` / `don't stop` | 「我要睡了」「别停，一直跑完」 | `stepping away` | 「我先走开一会儿」 |
| `babysit this` / `get it green` | 「盯着这个 PR」「把它跑绿」 | `land the stack` | 「把这叠 PR 合入主干」 |
| `check on PR X` | 「看看 PR X 现在什么情况」 | `catch me up` | 「同步一下最新进展」 |
| `tear this apart` / `challenge this` | 「往死里挑刺」「找找盲区」 | `new task` | 「切新任务」 |
