### Autopilot-stack

按 `Autopilot-full` playbook 执行，但不做合入。

1. **用「停在验证通过」替代第 5 步。** 当每个 PR 在当前 head 都已验证通过且 CI 全绿时停手，把这批 PR 交到操作者手里。交接之后，没有操作者放行谁都不许再推代码。每一轮 `/loop` 的 tick `prompt` 里都必须点明本文件，确保每轮巡检都牢记「禁止合入」这条规则。
2. **只有某个 PR 真正建立在另一个 PR 的改动之上时才叠栈。** 这是对第 3 步的唯一例外。按 `playbooks/opening-a-pr.md` 把它的 base 设成父 PR 分支而非主干。对应地，第 2 步的 rebase 改为：每个子 PR rebase 到父 PR 分支，只有栈底根 PR rebase 到主干。下层 PR 出现新 head 时顺带重叠上面的 PR；重叠后 `git patch-id` 没变的 PR 保留原有判定。

**Reply：** 列出每个 PR 及其判定结论，代替「已合入项」。
