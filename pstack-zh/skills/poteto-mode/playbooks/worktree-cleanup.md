### Worktree and simulator cleanup

1. 先拍快照并做审计。记下 `df -h /`，然后运行 `scripts/worktree-audit.sh [-b <pr-base-ref>] [repo-path]`（遵循 `principle-build-the-lever`）。不传 `-b` 时默认对照 `origin/HEAD` 判断是否 `MERGED`，如果 PR 指向别的基线分支就传 `-b origin/<branch>`。脚本从 `git worktree list` 读取路径，绝不靠手输，因为手输 `myrepo-worktrees/x` 会漏掉藏在 `.cursor/worktrees/myrepo/x` 里的目录（遵循 `principle-encode-lessons-in-structure`）。它会按体积、存在时间、合入状态、未提交改动、PR 状态和最近碰过它的对话对每个 `worktree` 分类并给出建议分组。扫描历史记录比较慢，放后台跑。
2. 建议分组只是参考，不是删除许可。真正权威的是当前置顶和活跃的对话列表（遵循 `principle-prove-it-works`）。从用户那里或侧边栏拿齐这份清单，逐个交叉核对候选目录。脚本以前就曾把用户置顶对话正在用的 `worktree` 标成 `safe`，所以一切以置顶活跃清单为准。
3. 删之前核实是否仍在使用。对每一行标成 `verify-recent-chat` 或你心里存疑的目录，扇出子代理去读对话记录，汇报该对话是不是置顶或仍在进行中，以及它实际碰了哪些 `worktree`（遵循 `principle-guard-the-context-window`，对话记录体积大）。一个置顶对话常常会通过后台子代理把 `arena` 和复现目录开进旁边的兄弟 `worktree`，那些目录即使名字没出现在侧边栏里也依然在用。按 `Subagents` 一节选好子代理推理档位。
4. 遇到不可逆损失先停下来问。`wip:N` 代表有 N 处已跟踪文件的未提交改动，必须先展示 `diff` 等用户拍板，因为干净的 `worktree` 删了还能从分支恢复，未提交改动删了就彻底没了。`scratch:N` 是未跟踪的临时文件，通常能删，但也要报出文件名。按 Autonomy 原则：干净、已合入且无对话占用的直接删；带 `wip` 或仍在使用的先停下确认。
5. 清理已确认的集合。逐个路径执行 `git worktree remove --force <path>`；如果目录因为 gitignored 构建产物残留在磁盘上，再 `rm -rf` 清掉，最后跑 `git worktree prune`。分支引用都还在，不会丢任何 commit。清完重跑 `df -h /` 并重新列出目录确认。
6. 模拟器和其他大头空间回收。模拟器往往是仅次于 `worktree` 的空间大户：`xcrun simctl --set testing delete all`（清 XCTestDevices 克隆）、`xcrun simctl delete unavailable`，以及 `xcrun simctl runtime list` 后用 `runtime delete <id>` 删掉老旧运行时。还不够时继续查：Xcode 的 `DerivedData` 和 `iOS DeviceSupport`、`~/Library/Application Support/Cursor`（里面的 `state.vscdb.backup`，以及按工作区目录名命名的 `snapshots/roots/<root>` 很容易膨胀）、包管理器缓存（pnpm、uv、brew、yarn）。只清理用户没交代保留的缓存。

这是唯一一个会直接删除用户本地状态、且没有 Code Review 兜底的 `playbook`，因此上面这几道门禁本身就是审查。

**Reply：** 清理前后的 `df -h /` 对比与回收空间、已删掉的 `worktree` 列表，以及每个被保留目录的一句话理由（被哪个对话占用，或存在未提交改动）。
