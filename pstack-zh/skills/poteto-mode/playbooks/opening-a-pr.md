### Opening a PR

附在其他所有 `playbook` 末尾调用。

从主干分支拉出 Git `worktree` 干活，无关改动一律不混进来。Rebase 成小步、可独立合入的 commit。提交前先对 `diff` 跑一遍 `cursor-team-kit` 里的 `/deslop`。

标题格式为 `type(scope): subject`，核心改动落在具体符号上时直接点出真实符号名。正文写成一分钟就能看完的简报，控制在 40 行以内，按以下顺序使用 `##` 小节标题并省去空节：`## Why`、`## What changed`、`## Scope`、`## Tradeoffs`（只写评审人会追问的被否决备选方案）、`## Blast Radius`、`## Verification`。

后续依赖 PR 通过设置 base 分支叠栈。直接以 ready 状态打开 PR，调用当前运行环境的 PR 工具时传入 `draft: false`；没有内置 PR 工具时，用不带 `--draft` 的 `gh pr create`，或者在 Origin CLI 能解析当前仓库时用 `origin pr create --status open`。刚开出 PR 不会自动触发 `Babysit`。
