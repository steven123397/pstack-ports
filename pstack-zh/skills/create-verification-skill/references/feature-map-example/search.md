# Search notes

搜索功能允许用户按标题或正文文本查找笔记、打开匹配的笔记，并清晰区分「无匹配结果」和「搜索服务不可用」。

## Sub-features

- `search-open` 从每个受支持的浏览器入口打开搜索框。
- `search-match` 返回标题和正文匹配结果，且不修改笔记数据。
- `search-open-result` 在笔记编辑器里打开一条搜索结果。
- `search-empty` 对无匹配的查询展示完整的空状态提示。
- `search-clear` 清空查询词并恢复最近笔记视图。
- `search-cli` 从终端返回一致的匹配笔记列表。

## How to get to it (user POV)

- 点击浏览器工具栏里的 `Search` 按钮。
- 焦点不在可编辑输入框内时，在浏览器按快捷键 `/`。
- 在终端运行 `notes search <query>`。

## Driving it with control-notes

Preconditions:

- Notes 在 `http://127.0.0.1:4173` 运行健康。
- 一次性数据目录中包含标题为 `Quarterly plan`、正文含 `Draft budget` 的笔记。
- `control-notes doctor` 报出预期的 URL 和数据目录。

- **工具栏入口。** 点击 `Search` 按钮。运行 `control-notes browser click --role button --name "Search"`。弹出名为 `Search notes` 的对话框，且焦点落在搜索框里。
- **快捷键入口。** 关闭对话框，让页面获得焦点后按 `/`。运行 `control-notes browser press --key "/"`。弹出同一个搜索对话框，且页面不会插入斜杠字符。
- **标题匹配。** 输入 `quarterly`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "quarterly"`。`Search results` 列表包含 `Quarterly plan`，不包含 `Grocery list`。
- **正文匹配。** 将查询词替换为 `budget`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "budget"`。结果里仍显示 `Quarterly plan`，并带正文命中摘要。
- **打开结果。** 点击 `Quarterly plan`。运行 `control-notes browser click --role link --name "Quarterly plan"`。搜索对话框关闭，编辑器标题变为 `Quarterly plan`。
- **空结果状态。** 重新打开搜索并输入 `volcano`。运行 `control-notes browser fill --role searchbox --name "Search notes" --value "volcano"`。搜索完成后出现名为 `No matching notes` 的状态提示。
- **清空查询。** 点击 `Clear search`。运行 `control-notes browser click --role button --name "Clear search"`。搜索框清空，`Recent notes` 区域替换掉原来的结果列表。
- **CLI 命中。** 在终端搜索。运行 `control-notes cli -- notes search "quarterly" --format json`。退出码为 `0`，stdout 包含一个标题为 `Quarterly plan` 的对象。
- **CLI 无结果。** 搜索不存在的关键词。运行 `control-notes cli -- notes search "volcano" --format json`。退出码为 `0`，stdout 为 `[]`。
- **留存实证。** 截取有结果的搜索状态。运行 `control-notes browser snapshot --aria --path artifacts/search/results.aria.txt` 和 `control-notes browser screenshot --path artifacts/search/results.png`。两份产物都明确显示 Notes 应用标识、查询词和 `Quarterly plan`。

## Gotchas

- 焦点在编辑器或搜索框里时按 `/` 只会输入字符，不会触发打开搜索。
- 搜索结果有短暂防抖延迟，请等待结果列表或空状态元素出现，不要写死 sleep。
- 已归档笔记默认不参与搜索，除非用户勾选 `Include archived`。
- CLI 默认输出人类可读格式，做稳定断言时务必传 `--format json`。
- 点击打开一条结果会改变浏览器当前页面状态，验证下一条查询前要先重新打开搜索。
