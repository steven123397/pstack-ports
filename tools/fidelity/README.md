# 工具：移植保真度检查

三个只读脚本，用来回答同一个问题：把 skill 包从 A 平台搬到 B 平台之后，行为还在不在。

它们不判断语义好坏，只把人工判断需要的证据准备齐。语义判断仍要看 diff 的正文。

## 1. 差分清单

```bash
python tools/fidelity/diff_bundle.py \
  --upstream D:/codex_project/upstreams/pstack/pstack \
  --port pstack-omp \
  --subdir skills \
  --out %TEMP%/fidelity
```

按相对路径配对两个树，每个有差异的文件写一份 unified diff，再写 `MANIFEST.tsv`（状态、上游行数、改动行数）。二进制文件记为 `BINARY`，不做文本 diff。

输出末行给出改动集中在哪些文件，按改动行数排序。先读这几个文件即可。

## 2. 引用完整性

```bash
python tools/fidelity/check_port.py --port pstack-omp --allow url
```

检查四类引用是否落地。

- Markdown 链接（相对路径）。
- 反引号里的 `references/`、`scripts/`、`playbooks/`、`assets/` 路径。
- `../<skill>/SKILL.md` 形式的跨 skill 引用。
- `skill://<skill>[/path]` 内部 URL。

再检查每个 `SKILL.md` 的 frontmatter：`name` 必须等于目录名，键必须在允许集合内。有失败时退出码为 1，可以直接当闸门用。`--allow` 接受子串，用来放行模板占位这类已知例外。

## 3. 结构对比

```bash
python tools/fidelity/outline_compare.py \
  --upstream D:/codex_project/upstreams/pstack/pstack \
  --port pstack-omp \
  --subdir skills \
  --ignore bugbot-triage
```

比较每对文件的小节数与编号步骤数。port 少于上游就判失败，等于或多于都放行，多于会列出增量，因为新增一步是允许的，丢一步不行。

比对按数量而不是标题文本，所以改编号、换措辞、重命名小节都不算差异。`--ignore` 用来跳过已知的改名文件。

## 通过标准

对当前仓库，三个脚本的期望输出如下。

```
files 136  same 79  diff 54  new 2  gone 1  binary 0
changed lines 739 of 12275 upstream lines (6.0%)

skills 56  links 67  paths 66  refs 65  problems 0  allowed 1

compared 110 files, failures 0, files with additions 1, skipped 1
```

`problems 0` 与 `failures 0` 是硬条件。改动行数是信号，不是判据，它只说明该读哪些 diff。