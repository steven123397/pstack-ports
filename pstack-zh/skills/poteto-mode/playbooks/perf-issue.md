### Perf issue

**实测数据归你把关。负责规划、审查并核验所有数字。** 每一次优化都必须绑定实测数据，别光看源码脑补性能。

1. 通过对应的 control `skill` 抓一份基线 trace。基线数字和之后的每一次测数，全部过一遍 **benchmark-checklist** `skill`。
2. 顺着代码追踪，让优化假设落到实处。没真跑过之前，别凭感觉宣称已经到了性能上限。
   按代价从低到高，依次尝试下面七条性能口诀：
   1. 干脆别做。与其把没人用结果的工作变快，不如直接停掉不做。
   2. 做一次，别重复做。
   3. 少做一点。
   4. 晚点再做。
   5. 趁用户没在等的时候做。
   6. 并行做。
   7. 换更省开销的做法。

   前面哪一条已经达标，就在那里停手。
3. 基于 trace 规划修复。如果改动跨越函数边界，先走 `architect`。把实现派给子代理，使用配置好的 `perf-issue` 模型（默认 `claude-opus-5-5-xhigh-fast`），并按 `Subagents` 一节选好推理档位。亲自审查 `diff`，再抓一份修复后的 trace。遵循 **sequence-verifiable-units** `principle`，每试完一个改动先验证，再试下一个。
4. 解析并对比前后产物（把 JSON 导进 sqlite 或做 diff）。报「结论未定（inconclusive）」或测错了端，一律不算通过，必须标出来。
5. 把实测对比数据写进 PR 描述。
6. 收尾执行 **Opening a PR**。

如果是围绕某个指标做持续多轮迭代优化，而不是一次性修掉单个慢点，改走 `Hillclimb` playbook（`playbooks/hillclimb.md`）。

**Reply：** 基线数字、修复后数字、变化幅度（delta）以及产物路径。
