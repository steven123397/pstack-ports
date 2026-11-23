# Create a note

创建笔记功能允许用户通过浏览器或 CLI 保存一条带标题的笔记、取消未完成的草稿，并从另一个面向用户的视图确认笔记已真实落盘。

## Sub-features

- `create-open` 从每个浏览器入口都能打开空白编辑器。
- `create-save` 持久化保存标题和正文。
- `create-cancel` 丢弃浏览器里未完成的草稿。
- `create-cli` 从终端创建同结构的笔记。

## How to get to it (user POV)

- 点击浏览器工具栏里的 `New note` 按钮。
- 焦点不在可编辑输入框内时，在浏览器按快捷键 `n`。
- 在终端运行 `notes create --title <title> --body <body>`。

## Driving it with control-notes

Preconditions:

- Notes 在 `http://127.0.0.1:4173` 运行健康。
- 当前不存在标题为 `Release checklist` 的笔记。
- `control-notes doctor` 报出预期的 URL 和一次性数据目录。

- **打开编辑器。** 点击 `New note`。运行 `control-notes browser click --role button --name "New note"`。出现名为 `Note editor` 的表单，且焦点落在 `Title` 输入框中。
- **输入内容。** 填写标题与正文。运行 `control-notes browser fill --role textbox --name "Title" --value "Release checklist"` 和 `control-notes browser fill --role textbox --name "Body" --value "Tag and publish"`。`Save note` 按钮变为可点击状态。
- **保存笔记。** 点击 `Save note`。运行 `control-notes browser click --role button --name "Save note"`。出现名为 `Note saved` 的状态提示，且标题显示 `Release checklist`。
- **确认持久化。** 返回笔记列表并重新打开这条笔记。运行 `control-notes browser click --role link --name "All notes"` 和 `control-notes browser click --role link --name "Release checklist"`。编辑器完整回显刚刚保存的标题和正文。
- **取消草稿。** 新建一条笔记，填入 `Discard me` 后点 `Cancel`。运行 `control-notes browser click --role button --name "New note"`、`control-notes browser fill --role textbox --name "Title" --value "Discard me"` 和 `control-notes browser click --role button --name "Cancel"`。页面回到笔记列表，且列表中没有 `Discard me` 链接。
- **CLI 入口。** 再创建第二条笔记。运行 `control-notes cli -- notes create --title "CLI note" --body "Created from terminal" --format json`。退出码为 `0`，stdout 包含新笔记的 ID 和标题。
- **留存实证。** 从 `All notes` 重新打开两条已保存的笔记。运行 `control-notes browser snapshot --aria --path artifacts/create-note/list.aria.txt` 和 `control-notes browser screenshot --path artifacts/create-note/list.png`。两份产物中均清晰可见 `Release checklist` 和 `CLI note`。

## Gotchas

- 焦点在文本框内时按 `n` 只会输入字母 `n`，不会打开新编辑器。
- 保存时会自动裁剪标题首尾空白，请断言最终渲染出的标题，而不是草稿输入框里的原始值。
- 单凭一条保存成功提示不算充分实证，必须退回列表重新打开笔记确认落盘。
- 清理测试数据时删掉 `Release checklist` 和 `CLI note`，但必须保留它们的实证产物。
