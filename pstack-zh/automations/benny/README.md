# benny

> 译自 cursor/plugins 0.15.29 `pstack/automations/benny/README.md`。本目录的 `skills/` 子目录与 `templates/` 是自动化源文件，自读版保留英文原文，见 `../../../../upstreams/pstack/pstack/automations/benny/`。

benny 给你两个处理 Slack issue 报告的 Cursor automation。一个分诊每份报告。另一个复现确认过的 bug，可能还会准备一份小的草稿修复。

这个目录里的文件是休眠的设置与自动化源。它们不会以 slash skill 的形式出现。

## 设置

1. 让 Cursor 指向 [`FOR_AGENTS.md`](./FOR_AGENTS.md)，并指定目标仓库。
2. 让 setup 把这整个目录合并进目标仓库的 `.cursor/automations/benny/`。必须保留仅存在于目标端的文件，冲突时要审阅合并，而不是覆盖本地改动。
3. 让 setup 在目标仓库的 `.cursor/settings.json` 里启用 pstack，作为共享依赖：

```json
{
	"plugins": {
		"pstack": { "enabled": true }
	}
}
```

4. 用户自有的配置放在拷贝出来的 pack 之外，例如 `.cursor/benny/`。参照 [`configuration.example.yaml`](./templates/configuration.example.yaml) 和 [`feature-map.example.md`](./skills/reproduce-and-fix-issues/references/feature-map.example.md)。
5. 启用任何一个 automation 之前，先把 `.cursor/settings.json`、`.cursor/automations/benny/` 和所有不含密钥的配置提交进 git。
6. 在编辑器里审阅每份新的 automation 草稿，或更新已有的 automation。然后发一条无害的测试报告，确认每个源频道的帖子都留在原线程里。
