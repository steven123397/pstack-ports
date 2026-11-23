# 渲染状态图

用 npm 包 `pele@1.9.0` 渲染要展示给用户的每一个 `.mmd` 文件，把生成的 SVG 交给用户。在仓库目录之外安装一次 Pele 即可。每个 SVG 写在对应 `.mmd` 文件同目录、同名。API 文档见 https://pele.run/api。调用 `render` 时传入选项 `{ limit: 1_000_000, outputLimit: 8_000_000, maxEdges: 10_000 }`，因为 Pele 的默认上限装不下 500 个状态的大图。如果 Pele 抛出 `PeleError`，把 Mermaid 文本和报错一起展示给用户。

## 配色与暗色模式适配

Pele 会忽略 Mermaid 的 `theme` 和 `themeVariables`，需要直接在 `.pele` 上设置 `--pele-*` CSS 变量，完整变量列表见 https://pele.run/theming。脚本会给每个状态打上所属分组的颜色类名（如 `class sN teal`），给违规状态打上 `class sN breaks` 或 `class sN mayBreak`，给最短 bug 路径上的每个状态打上 `class sN bugPath`，给 `PROPERTY` 反例里无限循环的每个状态打上 `class sN repeats`。Pele 会把这些类名直接挂在状态节点上，用 CSS 给这些类名上色即可。

`.mmd` 文件自带了 `breaks` 和 `mayBreak` 的 `classDef`，确保放进任何普通 Mermaid 查看器都能看清违规标记；分组颜色、`bugPath` 和 `repeats` 则没有 `classDef`。Pele 会把每条 `classDef` 颜色写成节点上的行内 `style` 属性，而行内 `style` 优先级高于普通 CSS 规则，因此下面给标记写的 CSS 规则必须加 `!important`，否则切到暗色主题后还会残留亮色标记底色。违规标记改填充色和文字色，`bugPath` 和 `repeats` 改边框。把标记规则排在分组颜色后面，让违规标记压过普通分组色。

下面是一套推荐配色（沿用旧版 `skill` 方案）。把它们放进每个 SVG 开头的 `<style>` 元素里，SVG 就能自动跟随查看器的亮色或暗色主题切换。

```css
.pele {
  --pele-bg: #ffffff;
  --pele-fg: #1c1c1c;
  --pele-muted: #656565;
  --pele-line: #808080;
  --pele-surface: #fcfcfc;
  --pele-surface-alt: #f1f1f1;
  --pele-border: #c9c9c9;
}
.pele .blue rect { fill: #c3e0ff; }
.pele .orange rect { fill: #f0d3bf; }
.pele .purple rect { fill: #e3d5ff; }
.pele .yellow rect { fill: #f0dcbf; }
.pele .teal rect { fill: #bfe3df; }
.pele .tan rect { fill: #e5d9ce; }
.pele .pink rect { fill: #ffcbe6; }
.pele .breaks rect {
  fill: #ffecee !important;
  stroke: #e72e3b !important;
  stroke-width: 2.5px !important;
}
.pele .breaks text {
  fill: #cd2834 !important;
}
.pele .mayBreak rect {
  fill: #fff3e6 !important;
  stroke: #e8730c !important;
  stroke-width: 2.5px !important;
}
.pele .mayBreak text {
  fill: #b85a06 !important;
}
.pele .bugPath rect {
  stroke: #1680f3 !important;
  stroke-width: 2.5px !important;
}
.pele .repeats rect {
  stroke: #9b35d6 !important;
  stroke-width: 2.5px !important;
  stroke-dasharray: 6 3;
}
@media (prefers-color-scheme: dark) {
  .pele {
    --pele-bg: #1f1f1f;
    --pele-fg: #f5f5f5;
    --pele-muted: #acacac;
    --pele-line: #939393;
    --pele-surface: #121212;
    --pele-surface-alt: #2c2c2c;
    --pele-border: #4e4e4e;
  }
  .pele .blue rect { fill: #1b3857; }
  .pele .orange rect { fill: #573117; }
  .pele .purple rect { fill: #3c2e57; }
  .pele .yellow rect { fill: #573d17; }
  .pele .teal rect { fill: #174641; }
  .pele .tan rect { fill: #3d3127; }
  .pele .pink rect { fill: #57233e; }
  .pele .breaks rect {
    fill: #2e2021 !important;
    stroke: #cf2b35 !important;
  }
  .pele .breaks text {
    fill: #ff6463 !important;
  }
  .pele .mayBreak rect {
    fill: #2e2619 !important;
    stroke: #d0700f !important;
  }
  .pele .mayBreak text {
    fill: #ffa257 !important;
  }
  .pele .bugPath rect {
    stroke: #116dd2 !important;
  }
  .pele .repeats rect {
    stroke: #9a3fcf !important;
  }
}
```
