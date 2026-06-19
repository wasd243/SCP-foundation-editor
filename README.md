# SCP Foundation Editor

<div align="center">
<img src="src-tauri/icons/icon.png" alt="SCP Foundation Editor" width="128" height="128">
</div>

<div align="center">

![License](https://img.shields.io/badge/license-AGPLv3-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-beta-orange)
![Downloads](https://img.shields.io/github/downloads/wasd243/SCP-foundation-editor/total)

</div>

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
> [Why `[[include]]` cannot be WYSIWYG](docs/What_the_hell_did_Wikidot_do_on_your_include.md) for the full explanation.

## Features

- **Visual editing** — headings, bold/italic/underline/strikethrough, sub/superscript, alignment
- **Blockquotes** — supports `[[div class="blockquote"]]` and `> ` syntax
- **Tables** — full table editing with header rows
- **Code blocks** — with language labels and basic syntax highlighting
- **Footnotes** — Wikidot-style footnotes with a dedicated side panel
- **Tabviews** — `[[tabview]]` / `[[tab]]` as editable tabs
- **Redacted spans** — custom `[[span]]` components (e.g. blackout/redaction styling)
- **Module Rate / User** — placeholder components for rating boxes and user tags (tip: the `[[user]]` component is an ugly placeholder, only for generating `[[*user ]]`, if you want to see the user with correct rendering, please go to Wikidot)
- **Autosave** — automatic local file saving while you write
- **Export** — push your content back to clean Wikidot wikitext
- **Fully local** — runs entirely offline; your work never leaves your machine

## Screenshots

<div align="center">

</div>

<!-- Replace with your actual screenshot path -->

## On `[[include]]` — Why It Cannot Be WYSIWYG

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

For the full argument — including the classification of `#include` / `@import` /
`use` / `import` / `[[include]]` by reversibility, and why nesting makes it
information-theoretically hopeless — see
**[the full write-up in `docs/`](docs/What_the_hell_did_Wikidot_do_on_your_include.md)**.

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
