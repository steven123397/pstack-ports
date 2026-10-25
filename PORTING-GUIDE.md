# 把 skill 包移植到另一个 agent harness

这份文档记录 pstack 从 Cursor 插件移植到 omp 的完整做法、实测数据和踩过的坑。下一次把同一个包移植到 codex、kimicode、zcode 或别的 harness 时，从这里的判断和脚本开始，不必重新摸索。

产物本身在 [`pstack-omp/`](pstack-omp/)，包级决策记录在 [`pstack-omp/ADAPTATION.md`](pstack-omp/ADAPTATION.md)。本文只讲可移植的方法。

## 产物状态

状态、最后确认时间与验证方式统一记在 [`docs/status.md`](docs/status.md)。本文不复制那张表——复制会漂移。恢复某个 port 时，先按下面第 5 步重跑三个脚本，再信那里的描述。

## 三种移植姿态，以及为什么选编译期改写

上游 pstack 自带的 `docs/harness/claude-code.md` 采用运行时映射表。skill 正文保留 Cursor 写法，模型执行时查表翻译。移植到 omp 时没有沿用，改成了编译期改写，正文直接写目标平台的机制。

| 姿态 | 做法 | 代价 |
| --- | --- | --- |
| 运行时映射 | 正文不动，另写一张映射表，每次会话读一次 | 模型会跳过读表；字段写错时 schema 直接拒绝，静默漂移 |
| 编译期改写 | 正文里的工具名、路径、模型、字段全部改成目标平台写法 | 上游更新后要按 diff 增量重做 |
| 双轨 | 两套正文并列 | 两条都要维护，很快分叉 |

选编译期的原因有三条。skill 被注入时是全文注入，正文写对一次就长期有效。映射错误的后果是任务被 schema 拒绝，而这类错误在运行时翻译里最难发现。改写的成本可以摊薄，因为上游 91% 的正文逐字节不变，只有约 6% 需要动。

代价要接受下来。上游每次发版，用差分脚本重新跑一遍，只处理有差动的文件。

## 六步流程

### 1. 固化基线

上游仓库保持只读：pin 记在 `UPSTREAM.json`，运行 `node tools/upstream/sync.mjs` 把它拉到 `.upstream/cursor-plugins/pstack`（`.upstream/` 不进 git）。产物是同一个 git 仓库里的子目录 `pstack-omp/`。上游 commit 记进 `ADAPTATION.md` 开头。

这样做的目的只有一个，任何一行产物都能回答"它对应上游哪一行"，增量移植靠 `git diff` 驱动。

### 2. 写平台差异清单

在产物里建 `docs/harness/<platform>.md`，用表格覆盖五块内容：工具名、子代理字段、模型路由、路径换算、无对应物的功能。

无对应物的功能要给出处理方式，跳过还是替代，以及跳过的固定措辞。这张表是后续所有改写的唯一依据，skill 正文和它冲突时以表为准。

### 3. 机械改写

按文件改，不按概念改。工具名、路径、命令前缀、字段名逐项替换，然后跑一次禁词扫描。

禁词表就是上游机制词的集合，例如 `subagent_type`、`AskQuestion`、`run_in_background`、`.cursor`、`agent-transcripts`。清零之后才进入安装验证。剩下的命中必须逐条解释，例如 watch-pr 代码里用 bugbot 作者名判定评审线程来源，那是功能，不是残留。

### 4. 安装冒烟

先 `omp plugin link ./pstack-omp`，再验证四件事：skill 能被 `skill://` 读出来、playbook 引用能解析、agent 出现在 task 工具描述里、`omp plugin doctor` 没有报错。

doctor 全绿不等于装好。见下面第 1 条教训。

### 5. 语义审查

这是最容易做假的一步。做法是先造差分，再分片交给不同模型家族，最后由一个人复核每一条结论。

```bash
python tools/fidelity/diff_bundle.py --upstream <上游根> --port pstack-omp --subdir skills --out %TEMP%/fidelity
python tools/fidelity/check_port.py --port pstack-omp --allow url
python tools/fidelity/outline_compare.py --upstream <上游根> --port pstack-omp --subdir skills --ignore <改名文件>
```

分片按语义聚而不是按文件数平摊，本次切成五片：核心 mode 与全部 playbook、references 与脚本、help 与 setup、其余 skill、agents 与打包。

每个审查席位只回答一个问题：这处改动是否保留了上游的规则、步骤、触发词、闸门。给出四分类。

- `MAPPED`，映射表覆盖的替换，附上是哪一条。
- `LOSS`，删掉或削弱了一条规则，没有平台必然性。
- `DRIFT`，指令还在，但行为变了，例如闸门条件、步骤顺序、角色职责。
- `INVENTION`，新增了一条会改变行为的规则。

每条结论必须带两端原文引用和行为后果。没读原文的结论不算。两个模型家族独立命中同一条，才算高置信。最后复核时，单家族命中要自己回到原文确认，确认不了就降级。

### 6. 整改与分发

审查结果按单元提交，一次一个可验证的变化。整改完再跑一遍第 5 步的三个脚本，然后在新进程里读回修正后的文本。

分发用仓库根的 marketplace catalog。消费者两条命令。

```
omp plugin marketplace add <owner>/<repo>
omp plugin install <name>@<catalog>
```

包内不要放 root `plugin.json`，原因见教训 1。

## 本次实测数据

| 指标 | 数值 | 再生命令 |
| --- | --- | --- |
| skill 目录 | 56 对 56，同名 | `ls pstack-omp/skills | wc -l` |
| playbook | 23 对 23，结构零丢失 | `outline_compare.py --subdir skills/poteto-mode/playbooks` |
| skill 文件 | 136 项，逐字节相同 79，有差异 54，新增 2，改名 1 | `diff_bundle.py --subdir skills` |
| 改写行数 | 739 / 12275，占 6.0% | 同上 |
| 引用检查 | 链接 67、路径 66、跨 skill 引用 65，问题 0 | `check_port.py` |
| 审查产出 | 需修 10 条，权衡 3 条，备注 5 条 | 见各切片报告 |

改写行数只用来定位该读哪些文件，不用来衡量质量。6% 里包含一次改名（142 行）和一个新增适配器（300 行），真正的语义改动不到 250 行。这个数字也随每次整改变化，本次整改后从 691 升到 739。

## 十条教训

**1. 包格式选错会静默丢 skill。** 加上 root `plugin.json` 后，56 个 skill 只剩 1 个能加载，`omp plugin doctor` 仍然报全绿。原因是包格式一旦被识别成 agent-plugins，就套用 Agent Skills 的封闭字段集，`disable-model-invocation` 不在集内，带这个字段的 skill 被丢弃。做法是只保留 `package.json` 的 manifest，分发走 marketplace catalog，并在安装后用 `skill://` 逐个命中，不要只看 doctor。

**2. 换行策略是交付内容，不是个人偏好。** 仓库没有 `.gitattributes`，而本机 `core.autocrlf=true`，两个 `.sh` 提交后 checkout 回 CRLF，从 WSL 经 `/mnt/d` 执行报 bad interpreter。修法是加 `*.sh`、`*.bash`、`*.mjs`、`*.ts` 的 `text eol=lf`。注意换行转换本身可能不产生 diff，因为 index 里早就是 LF，所以修复只能靠属性，不能靠再提交一次。

**3. 机制真伪要文档加二进制双证。** `/loop --until` 在 omp 文档里查不到，用 `grep -a -o` 在二进制里找到了提示原文，才确认可用。反向的例子是 `plan.enabled`，文档写它"启用 plan mode"，看起来是隔离的前置条件，实际它只管模式是否可用，真正决定会话从 plan 模式开始的是 `plan.defaultOnStartup`。查错一次就会对默认配置的用户误报。

**4. 默认值会改变语义，不只是能力。** `task.isolation.enabled` 默认关闭，关闭时 `isolated` 字段根本不存在，于是依赖它的四个 skill 静默退化成共享 checkout。`task.isolation.apply` 默认开启，开启时每个隔离 worker 的补丁在结束时自动落进当前 checkout，与"先验证后落地"的顺序相反。两个默认值都要写进 harness 文档的设置表，并用一次真实 spawn 验证落点，不要靠读代码推断。

**5. 全局设置只检测、经同意再写。** setup 类 skill 的契约通常只管自己那几个键。本次给 setup-pstack 加了隔离检查，但写成"读值、说后果、问一次、同意才写"，并且明确不动用户没同意过的 `task.*` 键。原文里"其余行逐字节不变"的承诺要同步改写，否则前后步骤互相矛盾。

**6. 宿主路径会藏在 verbatim 提示词里。** tick 提示词写着"每轮从 trunk 重读执行 playbook"，而 checklist 已经改成 `skill://`。上游这样写是因为它的仓库 vendor 了 playbook，port 没有。verbatim 指的是使用这段文字，不是禁止改这段文字。凡是"从仓库读"的说法都要换成可解析的 `skill://` 路径。

**7. 改名要全量核对引用。** 一个 `bugbot-triage.md` 改成 `review-triage.md`，涉及 playbook、SKILL、参考文件三处引用。引用检查脚本就是为这类改名准备的硬闸门，改完就跑。

**8. 只读保证分工具级和指令级，一个 agent 多职责时不可两全。** 上游 `readonly: true` 是工具级限制。port 的 `pstack-judge` 同时承担最难的代码改写，禁写会打断它，所以审查席位的只读只能靠 brief 加 `git status` 复核。做法是把差别写进文档，并用一个专门的白名单 agent（`pstack-reader`）承担真正需要工具级只读的探索任务。不要声称做不到的保证。

**9. 自述文档会腐化。** `ADAPTATION.md` 开头写着 55 skills、24 playbooks，实测 56 和 23，而且和同一文件后面的验证记录自相矛盾。凡是计数、路径、默认值，都配一条再生命令，审查时抽查五条。

**10. 审查 rubric 不区分 MAPPED 和 DRIFT，就什么都审不出来。** 没有分类时，审查者会把所有差异归为"平台适配"然后判 PASS。四分类加上两端引用，才能把"措辞变了"和"闸门条件变了"分开。本次 10 条需修里有 1 条会实际削弱行为（隔离默认关闭），其余是文档与措辞，这个比例只有做了分类才看得出来。

## 下一次的最小动作

1. 复制五张映射表，先写 `docs/harness/<platform>.md`，再动 skill 正文。
2. 跑 `diff_bundle.py`，按改动行数排序，从最大的文件开始读。
3. 跑 `check_port.py` 和 `outline_compare.py`，两个都要 0 失败。
4. 按语义切成三到五片，交给两个模型家族审查，用四分类 rubric，要求引用两端原文。
5. 自己复核每条 `LOSS`、`DRIFT`、`INVENTION`，再决定改不改。
6. 整改后重跑三个脚本，另开进程从安装副本读回修改过的段落。
7. `omp plugin link` 与 marketplace 两条安装路径各走一次，`skill://` 命中数要等于 skill 目录数。

## 未解项

- Jules 适配器只做了静态核对。真实 API 需要 `JULES_API_KEY` 和已授权的 GitHub 仓库，本机没有。
- 多模型面板最多两席，因为只有三个 `pstack-*` 角色，第二个面板席位与非面板席位必然同族。
- 验证者与写作者的模型家族独立性只对本地 spawn 成立，Jules 会话选不了模型。
- `task.isolation.apply` 取 true 还是 false 是全局取舍。pstack 需要 false，别的 skill 可能希望自动落地。

## 工具

上游拉取在 [`tools/upstream/sync.mjs`](tools/upstream/sync.mjs)，按 `UPSTREAM.json` 的 pin 工作；`--check` 只报告落后多少提交。三个保真脚本在 [`tools/fidelity/`](tools/fidelity/)，用法与通过标准见同目录的 `README.md`。它们只读，任何时候都可以重跑。