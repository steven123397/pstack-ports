# Bugbot 分诊指南

当 `Babysit` playbook（`../playbooks/babysit.md`）处理 Bugbot 或自动评审工具留下的评论时，按这份参考执行。目标不是一刀切无视 Bugbot，而是改掉「只要机器人留了评论就必须改代码」的惯性。

## 判定准则

动手前先把每条 Bugbot 评论线程归入三类之一：

- `fix`：评论指出了站得住脚的正确性、安全、隐私、数据丢失、鉴权、计费、migration、幂等性、并发竞争或上线行为问题。在拥有这段代码的最底端 PR 里修好，回复贴上 commit SHA 并 resolve 该线程。
- `dismiss`：评论命中了已归档的低风险噪音模式，且当前代码和上下文能证明不需要改代码。写一句简明理由回复并 resolve 该线程。
- `ask`：评论属于新类型、高严重级、涉及安全/隐私/数据，或模棱两可。直接问用户，不要瞎猜。

拿不准就选 `ask`。漏掉一条吹毛求疵的风格评论代价很小，放过一个真数据或安全 bug 代价极大。

## 经验模式记录格式

以后补充新模式时统一用这个格式：

```markdown
### <简短模式名称>

- Confidence: candidate | recurring | strong
- Skip when: <必须同时满足的跳过条件>
- Do not skip when: <绝对不能跳过的风险红线>
- Example signal: <用来识别该模式的典型措辞或代码上下文>
- Source: <PR/评论链接或简短历史记录>
```

有一两个实例标 `candidate`，多次真实驳回后升为 `recurring`，只有范围窄、反复验证且低风险的模式才标 `strong`。

## 常见可跳过候选模式

### 刻意为之的 UI 或设计系统视觉改动

- Confidence: candidate
- Skip when: PR 描述、截图、设计评审或周边代码已经明确说明了这项视觉改动，而 Bugbot 评论只是在复述「某个共享视觉默认值变了」。
- Do not skip when: 评论指向无障碍访问、焦点可见性、键盘导航、色彩对比度，或 PR 并未打算改动的组件 API 契约。
- Example signal: 围绕焦点轮廓、按钮尺寸、间距或共享组件默认样式的评论，且主理人回复过「intentional / intended（刻意为之）」。

### Bugbot 看不到的上层 PR 或栈内用法

- Confidence: candidate
- Skip when: Bugbot 把某个导出符号、组件、辅助函数或文件标成未使用，而当前托管平台的 PR 列表、`diff`、上层栈 `diff` 或 PR 上下文能证实栈里后面的 PR 用到了它。
- Do not skip when: 当前 PR 根本不在栈里、该符号属于公共 API，或所谓上层用法无法查证。
- Example signal: 报「Exported component is never used」，真人回复「used upstack（上层 PR 会用）」。

### 并行迁移期间的临时重复代码

- Confidence: candidate
- Skip when: PR 刻意保留一小段重复代码，是为了让新路径与正在被删除、替换或验证中的旧路径并行过渡。
- Do not skip when: 重复代码牵涉安全、计费、数据访问、API 行为，或者抽成长期共享抽象明显能降低风险。
- Example signal: 报「Significant duplication」或「duplicated validation logic」，而主理人解释旧路径马上要删或刻意先局部隔离。

### 现有框架或组件不变量已经兜住的警告

- Confidence: candidate
- Skip when: 评论担心的问题已经由当前 `diff` 或附近代码里可见的共享组件、框架契约、类型不变量或单一数据源保证了。
- Do not skip when: 这条不变量只是口头假设并未强制执行、依赖时序，或跨越了数值可能分叉的异步/状态边界。
- Example signal: 共享弹窗组件已经卡死视口高度，却报内部弹窗缺 `max-height`；或本地判空值和传参值来自同一源头却报空值风险。

### 主理人已明确声明的后续单或延后清理

- Confidence: candidate
- Skip when: PR 主理人明确说过这是已知的后续跟进项、当前 PR 没有让行为变糟，且问题不在高风险领域。
- Do not skip when: 代理在没有主理人表态的情况下自作主张、问题属于中高危产品行为，或推迟处理会合入新的行为回归。
- Example signal: 「I'll worry about that later」「we'll delete this eventually（后面再删）」。

### 机器人自己撤回或明说是误报的规则评论

- Confidence: recurring
- Skip when: 评论正文或 Bugbot 后续回复明确写着已撤回、已合规或属误报，且代理在本地核实过对应规则。
- Do not skip when: 没有任何解释，仅凭某个人对高风险问题随口说了一句「false positive」。
- Example signal: 一条文件命名规则评论，正文里自己就写着当前文件已经符合规范。

## 默认必须询问（Ask）的类别

以下几类绝不自动跳过，哪怕以前的 PR 曾经驳回过类似评论：

- 涉及安全、隐私、鉴权、计费、数据留存、训练数据和权限边界的问题。
- 高严重级问题。
- 涉及 migration、schema、幂等性、并发和跨系统行为的问题。
- 建议改法很小、明显能降风险且不改变产品意图的评论。

历史数据显示，真人偶尔会手动驳回安全或数据流相关的评论。那些属于主理人当场担责的个案判断，不能上升为全团队自动跳过规则。

## 近期盯盘提炼的候选经验

在 `Babysit` 期间或结束后，如果发现对团队有通用价值但还不够成熟的模式，先追加到这里；等几个 PR 反复印证后再升格进上面的正式小节。

### 手工重实现原生浏览器行为

- Confidence: candidate
- Skip when: 几乎从不跳过。只要一份 `diff` 用手工代码替代了原生浏览器行为（比如用 JS 定位克隆替代原生 sticky、用转发滚轮/触摸事件替代原生滚动目标、用 mask/clip-path 替代绘制顺序遮挡），Bugbot 针对这类代码抓出来的逻辑 bug 一贯非常准。
- Do not skip when: 评论涉及事件转发漏洞（wheel `deltaMode`、触控拖动、边缘滚动链、tap slop）、mask/clip 命中测试偏差，或 observer 与 React 状态更新之间的时序竞争。默认直接选 `fix`。
- Example signal: 「masks do not affect hit-testing」「overlay blocks wheel scroll」「ignores deltaMode」「runs in the IntersectionObserver callback before React applies state」。
- Source: 某次 sticky 遮挡修复 PR，连续跑了 6 轮 Bugbot、大约 18 条发现，无一例外全修了，一条没驳回。

### 契约测试漂移指控验证成本极低，先跑一遍测试再说

- Confidence: candidate
- Skip when: 绝不跳过验证本身，跑一遍就一条命令的事。当 PR 带了锁死协议或文档措辞的契约测试（比如对 `SKILL.md` 跑正则、给文档文案做快照），而 Bugbot 声称「测试已经跟文档对不上了」（或反过来），定性之前先在当前 PR tip 上直接跑一遍那个测试。跑红了就是实证坐实指控；跑绿了就是驳回回复里最硬的反证。
- Do not skip when: 不适用，这是一条核查捷径，不是跳过模式。注意前面「第三轮起倾向驳回」的经验启发在这里会误伤：锁死文档措辞的测试，恰恰就是因为前面几轮改了文档才漂移的。
- Example signal: 报「Contract test omits the pre-fix wait」，对应 PR 前几轮修复提交刚改写过被锁定的段落，在 tip 上一跑果然正好挂在那条断言上。
- Source: 某次锁死文案的 PR 跑了 8 轮 Bugbot，前面每轮都修通了，到第 7 轮那条指控照样是真的。

### 同一 PR 后续提交已经修掉的过期安全评审发现

- Confidence: candidate
- Skip when: 智能安全评审（或类似工具）声称少了鉴权或校验调用，但当前 PR tip 已经明确补上了完全一致的门禁（且带测试），通常是在评审跑完后另打的加固 commit 补上的。
- Do not skip when: 所指的辅助函数对当前主体其实是空操作、检查执行在它要保护的副作用之后，或者漏覆盖了所涉主体。
- Example signal: 报 HIGH 级「missing authorization check」，而最新 tip 上就在副作用之前已经调了对应校验。
- Source: 某次 webhook 接口 PR，加固提交落在安全评审跑完之后。

### 放宽刻意收窄的错误条件反而会掩盖真报错

- Confidence: candidate
- Skip when: 评论要求把一个刻意收窄的错误判断（特定 `errno`、错误码或状态类）放宽成兜底捕获，而这个收窄原本承载了真实语义区分。最典型的例子是仅在 `ENOENT` 时走依赖回退：「命令没安装」和「命令跑了但执行失败」是两码事。只要返回非零退出码就去跑回退，会把正常的业务失败（资源不存在、鉴权过期、网络断连）拿去重跑回退路径，最后报出回退路径的错，彻底盖掉真正原因。
- Do not skip when: 收窄条件漏掉了同一大类的情况（例如另一个代表「二进制不可用」的 errno 如 `EACCES`，或另一类传输层故障）、未处理分支会丢数据或留下半截状态，或者重试本身幂等且原始错误仍会完整浮出。
- Example signal: 报「only retries when X fails with ENOENT … never tries the fallback even when a working Y exists」，指向的恰是只针对缺失依赖而非命令失败才回退的代码。
- Source: 某次 CLI 重命名 PR，其回退逻辑本就只处理二进制缺失，不处理命令执行报错。
