# SCP Foundation Editor

<div align="center">

**English** / [简体中文](#scp-基金会编辑器)

</div>

<div align="center">
<img src="src-tauri/icons/icon.png" alt="SCP Foundation Editor" width="128" height="128">
</div>

<div align="center">

![License](https://img.shields.io/badge/license-AGPLv3-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-beta-orange)
![Downloads](https://img.shields.io/github/downloads/wasd243/SCP-foundation-editor/total)

</div>

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Why `[[include]]` Cannot Be WYSIWYG](#why-include-cannot-be-wysiwyg)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Building from Source](#building-from-source)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

A cross-platform **WYSIWYG editor** for writing SCP articles in Wikidot text,
built for the SCP-CN wiki community. Write your article visually — see headings,
blockquotes, tables, footnotes, tabviews, code blocks, and redacted spans render
as you type — then export clean Wikidot wikitext ready to paste into the wiki.

> [!IMPORTANT]
>
> This editor does **not** aim to render every Wikidot construct as WYSIWYG.
> In particular, `[[include]]` (resourcepack/theme formats) is **one-way only**
> and cannot be round-tripped through a visual editor. This is a structural
> limitation, not a missing feature — see
> [Why `[[include]]` cannot be WYSIWYG](docs/Include_block.md) for the full explanation.

## Features

- **Visual editing** — headings, bold/italic/underline/strikethrough, sub/superscript, alignment
- **Blockquotes** — supports `[[div class="blockquote"]]` and `> ` syntax
- **Tables** — full table editing with header rows
- **Code blocks** — with language labels and basic syntax highlighting
- **Footnotes** — Wikidot-style footnotes with a dedicated side panel
- **Tabviews** — `[[tabview]]` / `[[tab]]` as editable tabs
- **Redacted spans** — custom `[[span]]` components (e.g. blackout/redaction styling)
- **Module Rate / User** — placeholder components for rating boxes and user tags (tip: the `[[user]]` component is an
  ugly placeholder, only for generating `[[*user ]]`, if you want to see the user with correct rendering, please go to
  Wikidot)
- **Autosave** — automatic local file saving while you write
- **Export** — push your content back to clean Wikidot wikitext
- **Fully local** — runs entirely offline; your work never leaves your machine

## Screenshots

<img width="1916" height="1009" alt="image" src="https://github.com/user-attachments/assets/254f3b92-d224-49d9-a81f-131401cf22be" />
`Home` ribbon page and main editing area.

<br clear="both" />

---

<img align="right" width="380" height="154" alt="image" src="https://github.com/user-attachments/assets/e15d11cc-a171-4af1-944b-0b25626c881f" />
`Insert` ribbon page.

<br clear="both" />

---

<img align="right" width="518" height="141" alt="image" src="https://github.com/user-attachments/assets/6f3ce730-6d30-4cc6-8eee-6f3f53cc7e59" />
Simple `autosave` settings.

<br clear="both" />

---

## Why `[[include]]` Cannot Be WYSIWYG

`[[include]]` looks like C's `#include` or CSS's `@import`, but it is not.
Those are **textual substitution** with fixed content. `[[include]]` is a
**parameterized macro** — closer to Rust's `macro_rules!` — with variable
interpolation and silent fallback. Macro expansion is lossy, conditional, and
(when nested) irreversible: the same include with different arguments expands to
different output, so there is no way to reconstruct the original directive from
the rendered result.

A WYSIWYG editor would additionally require editing the expanded content and
syncing it back to source — but after expansion, template content, interpolated
arguments, and user-authored text are indistinguishable in the DOM. There is no
correct place to write an edit back.

I hardcoded `[[include :component:image-block]]` include WYSIWYG generator
and I used to want to do a resourcepack includer,
but now the resourcepack only works on parser rather than generator.

So now you can see a `.sql` file exists in `crates/ltmf/src/interpret/include/`.
That's my legacy version based on `{$ }` variables and meta data attacher
(already removed, that's an attacher for `data-editor-export` and `data-editor-include`).

I've given up on `resourcepack/` includer part, but that's not a trash folder because it only contains
`image-block.ftml` for resolving `[[include :component:image-block]]`, so I leave it alone.

For the full argument — including the classification of `#include` / `@import` /
`use` / `import` / `[[include]]` by reversibility, and why nesting makes it
information-theoretically hopeless — see
**[the full write-up in `docs/`](docs/Include_block.md)**.

## Tech Stack

- **[Tauri v2](https://tauri.app/)** — cross-platform desktop shell (Rust backend + WebView frontend)
- **[Vue 3](https://vuejs.org/) + TypeScript** — editor UI
- **[TipTap](https://tiptap.dev/) / ProseMirror** — the WYSIWYG editing core
- **[ftml](https://crates.io/crates/ftml)** — Wikidot text -> HTML parser (Rust), with a custom-patched build
- **Rust** — Wikidot/ftml processing pipeline, interceptors, and IPC commands

## Installation

Download the latest build for your platform from the
[Releases](https://github.com/wasd243/SCP-foundation-editor/releases) page.

| Platform | File                 |
|----------|----------------------|
| Windows  | `.exe`               |
| macOS    | `.dmg`               |
| Linux    | `.AppImage` / `.deb` |

## Building from Source

```bash
# Prerequisites: Rust, Node.js, and Tauri's platform dependencies
# See https://tauri.app/start/prerequisites/

npm install            # install frontend dependencies first
cargo tauri dev        # run in development
cargo tauri build      # produce a release build
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

Theme assets and logos used in this project are credited in
[CREDITS.md](CREDITS.md). All such assets remain under their original
licenses (CC BY-SA).

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.
See [LICENSE](LICENSE).

---

# SCP 基金会编辑器

<div align="center">

[English](#scp-foundation-editor) / **简体中文**

</div>

<div align="center">
<img src="src-tauri/icons/icon.png" alt="SCP 基金会编辑器" width="128" height="128">
</div>

<div align="center">

![License](https://img.shields.io/badge/license-AGPLv3-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-beta-orange)
![Downloads](https://img.shields.io/github/downloads/wasd243/SCP-foundation-editor/total)

</div>

## 目录

- [功能特性](#功能特性)
- [界面截图](#界面截图)
- [为什么 `[[include]]` 无法实现所见即所得](#为什么-include-无法实现所见即所得)
- [技术栈](#技术栈)
- [安装](#安装)
- [从源码构建](#从源码构建)
- [参与贡献](#参与贡献)
- [致谢](#致谢)
- [许可证](#许可证)

一款跨平台的、用于以 Wikidot 文本撰写 SCP 文章的**所见即所得（WYSIWYG）编辑器**，
为 SCP-CN 维基社区打造。你可以可视化地撰写文章——标题、引用块、表格、脚注、标签视图、
代码块以及涂黑（删改）文本会在你输入时实时渲染——随后导出干净的 Wikidot 维基文本，
可直接粘贴到维基中。

> [!IMPORTANT]
>
> 本编辑器**并不**追求将每一种 Wikidot 结构都实现为所见即所得。
> 尤其是 `[[include]]`（资源包 / 主题格式）是**单向的**，
> 无法在可视化编辑器中往返转换。这是一个结构性的限制，而非缺失的功能——
>
> 对此写了一篇简单的介绍
> [为什么 `[[include]]` 无法实现所见即所得](docs/Include_block.md)。

## 功能特性

- **可视化编辑**——标题、加粗 / 斜体 / 下划线 / 删除线、上下标、对齐
- **引用块**——支持 `[[div class="blockquote"]]` 和 `> ` 两种语法
- **表格**——完整的表格编辑，支持表头行
- **代码块**——带语言标签及基础语法高亮
- **脚注**——Wikidot 风格的脚注，附带独立侧边栏
- **标签视图**——`[[tabview]]` / `[[tab]]` 作为可编辑标签页
- **涂黑文本**——自定义 `[[span]]` 组件（例如涂黑 / 删改样式）
- **评分模块 / 用户**——评分框与用户标签的占位组件（提示：`[[user]]` 组件只是一个简陋的占位符，仅用于生成 `[[*user ]]`
  ，如果你想看到正确渲染的用户，请前往 Wikidot）
- **自动保存**——撰写时自动保存到本地文件
- **导出**——将内容导出为干净的 Wikidot 维基文本
- **完全本地**——完全离线运行；你的作品永远不会离开你的设备

## 界面截图

<img width="1916" height="1009" alt="image" src="https://github.com/user-attachments/assets/254f3b92-d224-49d9-a81f-131401cf22be" />
`主页`功能区页面与主编辑区域。

<br clear="both" />

---

<img align="right" width="380" height="154" alt="image" src="https://github.com/user-attachments/assets/e15d11cc-a171-4af1-944b-0b25626c881f" />
`插入`功能区页面。

<br clear="both" />

---

<img align="right" width="518" height="141" alt="image" src="https://github.com/user-attachments/assets/6f3ce730-6d30-4cc6-8eee-6f3f53cc7e59" />
简单的`自动保存`设置。

<br clear="both" />

---

## 为什么 `[[include]]` 无法实现所见即所得

`[[include]]` 看起来像 C 语言的 `#include` 或 CSS 的 `@import`，但它并不是。
那些是内容固定的**文本替换**。而 `[[include]]` 是一种**带参数的宏**——
更接近 Rust 的 `macro_rules!`——具有变量插值和静默回退。宏展开是有损的、有条件的，
并且（在嵌套时）不可逆：同一个 include 配以不同参数会展开为不同的输出，
因此无法从渲染结果重建出原始指令。

所见即所得编辑器还会额外要求对展开后的内容进行编辑并同步回源码——
但在展开之后，模板内容、插值的参数以及用户撰写的文本在 DOM 中已无法区分。
没有任何正确的位置可以写回一次编辑。

我硬编码了 `[[include :component:image-block]]` 这个 include 的所见即所得生成器，
我曾经想做一个资源包 includer，
但现在资源包只在解析器（parser）上生效，而非生成器（generator）。

所以现在你能在 `crates/ltmf/src/interpret/include/` 中看到一个 `.sql` 文件。
那是我基于 `{$ }` 变量的旧版本
（那是一个用于 `data-editor-export` 和 `data-editor-include` 的附加器）。

我已经放弃了 `resourcepack/` 的 includer 部分，但那并不是个垃圾文件夹，
因为它只包含用于解析 `[[include :component:image-block]]` 的 `image-block.ftml`，所以我保留了它。

`#include` / `@import` / `use` / `import` / `[[include]]` 的分类，以及为什么嵌套会使其在信息论意义上变得无望——

**[`docs/` 中的完整说明](docs/Include_block.md)**。

## 技术栈

- **[Tauri v2](https://tauri.app/)**——跨平台桌面外壳（Rust 后端 + WebView 前端）
- **[Vue 3](https://vuejs.org/) + TypeScript**——编辑器 UI
- **[TipTap](https://tiptap.dev/) / ProseMirror**——所见即所得编辑核心
- **[ftml](https://crates.io/crates/ftml)**——Wikidot 文本 -> HTML 解析器（Rust），使用自定义修补的构建
- **Rust**——Wikidot/ftml 处理流水线、拦截器以及 IPC 命令

## 安装

从 [Releases](https://github.com/wasd243/SCP-foundation-editor/releases) 页面
下载适用于你平台的最新构建。

| 平台        | 文件                   |
|-----------|----------------------|
| Windows   | `.exe`               |
| macOS     | `.dmg`               |
| Linux     | `.AppImage` / `.deb` |

## 从源码构建

```bash
# 前置依赖：Rust、Node.js 以及 Tauri 的平台依赖
# 参见 https://tauri.app/start/prerequisites/

npm install            # 先安装前端依赖
cargo tauri dev        # 以开发模式运行
cargo tauri build      # 产出发布构建
```

## 参与贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 致谢

本项目中使用的主题资源与徽标在
[CREDITS.md](CREDITS.md) 中注明。所有此类资源均保留其原始
许可证（CC BY-SA）。

## 许可证

基于 **GNU Affero General Public License v3.0 (AGPLv3)** 许可。
参见 [LICENSE](LICENSE)。
