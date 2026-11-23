---
name: unslop
description: "清理任何文字里的 AI 套话与机器腔。"
disable-model-invocation: true
---

# Unslop

修改文本，清除 AI 写作套路。对照下面的模式清单逐项扫描并重写。保住原意，贴合目标语境该有的语气。

## 需要扫描并修正的模式

规则编号是其他 `skill` 直接引用的稳定 ID，被移除的旧规则会留下空号，编号不要重排。

### 内容层

3. **浮于表面的伴随短语。** 英文里的 `"highlighting..."`、`"ensuring..."`、`"reflecting..."`、`"showcasing..."`、`"fostering..."`，以及中文里空洞的「彰显了……」「进一步赋能……」「有效保障了……」。直接删掉，或者拿真实出处展开说实话。
5. **含糊归因。** 英文里的 `"Experts believe"`、`"Industry reports suggest"`、`"Some critics argue"`，中文里的「业内普遍认为」「有观点指出」。点出具体来源，否则删掉。

### 用词层

7. **高频 AI 腔词汇。** 英文里的 `Additionally`、`crucial`、`delve`、`enduring`、`enhance`、`fostering`、`garner`、`interplay`、`intricate`、`landscape`（抽象用法）、`pivotal`、`showcase`、`tapestry`（抽象用法）、`testament`、`underscore`、`vibrant`，以及中文里对应的「至关重要的」「深入探讨」「赋能」「抓手」「闭环」「生态版图」。换成大白话。
8. **花哨地替代表「是 / 有」。** 英文里的 `"serves as"`、`"stands as"`、`"boasts"`、`"features"`，中文里的「充当了……的角色」「具备了……的特性」。直接说「是」或「有」。
9. **「不仅 X，而且 Y」套路（`"Not just X, but Y."`）。** 直接把重点说出来，别绕弯子。
10. **强凑三连排比（Rule of three）。** 别硬把所有观点都凑成三个一组，实际有几个就写几个。
11. **同义词轮换强迫症。** 一段话里把同一个对象来回换成「主角」「核心人物」「关键角色」「主人公」。定死一个名字，老老实实重复用它。
12. **假范围句式。** 写「从 X 到 Y」（`"from X to Y"`），但 X 和 Y 根本不在同一根标尺上。直接平铺列出来。

### 风格与标点

13. **滥用破折号。** 彻底避开长破折号，只用句号或逗号（别用括号、短破折号或拿连字符当破折号顶替）。如果两层意思需要切开，直接句号收尾，或者用逗号。
14. **滥用句中冒号。** 列表或例子前用冒号没问题，别拿冒号当句子中间的连接胶水。比如英文 `"If you're coming from traditional automation: instead of registering event handlers, you describe conditions"` 里这个冒号毫无作用。干脆拆掉对比铺垫、让观点自己站住，写成 `"Describing when the scheduler should fire works best as plain English."`。意思一模一样，少了拐杖标点。
15. **滥用加粗。** 别把每个专有名词或缩写都顺手加粗。
16. **复读式行内小标题列表。** 典型破绽是加粗标签加冒号，后面紧跟着把标签复述一遍，比如「**性能：** 性能提升了……」。直接改成正常叙述句。如果加粗开头以句号收尾、先点出条目名，后面紧跟的是真正的新信息（比如「**TypeScript 中的 Schema。** 所有表定义集中放在一个文件里。」），这种写法很清爽，不算套路。
17. **英文标题每个词首字母大写（Title case）。** 改用正常句首大写（sentence case）。
18. **装饰性 emoji。** 把标题和列表项里的装饰性表情符号全删掉。
19. **英文弯引号。** 写英文时统一用直引号（`"` 和 `'`）。

### 对话残留套话

20. **聊天机器人腔。** `"I hope this helps!"`、`"Let me know if..."`、`"Of course!"`、`"Certainly!"`、`"Found the smoking gun!"`，以及中文里的「希望这对你有帮助！」「如有需要请随时告诉我！」「当然可以！」「找到实锤了！」。全删。
22. **拍马屁语气。** `"Great question! You're absolutely right!"` 或「好问题！你说得完全正确！」。直接回答正事。

### 凑字废话

23. **冗余垫词。** `"In order to"` 改成 `"To"`，`"Due to the fact that"` 改成 `"Because"`，直接删掉 `"It is important to note that"` 和中文里的「值得注意的是」「综上所述」「基于以上考量」。
24. **过度叠甲留后路。** `"could potentially possibly be argued that it might"` 改成 `"may"`，中文里「在某种程度上或许有可能倾向于」直接改成「可能」。
25. **空洞展望式结尾。** `"The future looks bright."` 或「未来可期」。改成具体计划或客观事实。

### 黑话与抽象隐喻

26. **抽象隐喻名词。** 英文里的 `substrate`（直接说 base）、`wedge` / `wedge in`（add）、`vector`（way / method）、`locus`、`vantage`、`nexus`、当名词用的 `primitive`、当比喻用的 `harness`、如 `"API surface"` 里的 `surface`、`bedrock`、当比喻用的 `scaffolding`、`modality`、`paradigm`、`gold-plating`（超出实际需要的过度加工）、当比喻用的 `ratchet`（直接说机制原名，或只紧不松的下限）、把挪代码说成 `evacuate`（直接说 move out）、`endgame`（最后阶段）、`north star`、`flywheel`，以及中文里对应的「底座」「抓手」「北极星」「飞轮」「范式」。这些词听着像技术词，实际上都有更直白具体的说法，直接选具体词。

### 好好说人话

27. **说它到底干了什么，别说它「感觉怎么样」。** 「数据库触手可及」「读着顺手的 SQL」「紧跟 schema 的类型」说的都是虚无缥缈的感觉。改法是点出具体机制或数字，比如「`.toSQL()` 返回发往数据库的精确字符串」「改掉列名就会直接让构建失败」。问自己这句话到底让读者知道了什么或该去做什么，直接写出来。如果改写不成一条具体指令、事实或数字，直接删掉。再多加一道校验：如果这句话原封不动贴进别的项目文档里也照样成立，说明它对眼前这个项目什么都没说，直接删。
28. **把密不透风的长句拆短。** 如果读者读到一半还得倒回去重理语法结构，就把它劈成两句或砍掉多余从句。一句只说一件事。
29. **优先用主动语态。** 揪出「被……」或英文 `"is/are/was/were + 过去分词"`，把真正干活的主语点出来。比如 `"queries are validated"` 改成 `"the compiler validates queries"`，`"the file is parsed by the loader"` 改成 `"the loader parses the file"`，中文里的「文件被加载器解析」改成「加载器解析文件」。只有在动作发出者确实未知或真的不重要时，才用被动语态。
30. **砍掉水副词，或者换个更有力的动词。** `"runs quickly"` 改成 `"is fast"` 或直接给实测数字，`"significantly improves"` 改成实测增量，中文里的「显著提升」「快速运行」同理。靠副词硬撑一个软弱动词，说明动词本身就选错了。
31. **能用朴素词就别用装腔词。** `"utilize"` 和 `"leverage"` 改成 `"use"`，`"facilitate"` 改成 `"help"`，`"numerous"` 改成 `"many"`，`"in the event that"` 改成 `"if"`，中文里「依托」「借助」「予以」改回「用」「帮」「如果」。花哨的同义词几乎从来不会更清楚。
32. **拿腔拿调的文风。** 有直白说法却硬要玩比喻或抖机灵，包括装格言（「接上线，要么删掉」）、为了装酷故意写残缺断句、把代码拟人化（「计划托住了它」）、虚头巴脑的比喻动词（「搭便车」「立在……之上」），以及套路起手式。把「值得拧一拧的旋钮」直接改成「值得调整的参数」。心里想说什么就直接说什么。隐喻名词归第 26 条管。
33. **过度压缩成电报体。** 省掉主谓宾或冠词、写没动词的碎片、拿一堆符号和缩写逼着读者去破译而不是正常阅读。比如 `"Parser rejects bad date → exit 2, no write"` 改成 `"The parser rejects a bad date, exits with code 2, and writes nothing."`，中文同理写成完整人话：「解析器拒绝非法日期，以状态码 2 退出，且不写入任何内容。」老老实实写带主语和动词的完整句子，把箭头和生僻缩写摊开说清楚。
