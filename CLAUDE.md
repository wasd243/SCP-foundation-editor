# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a desktop WYSIWYG editor for SCP Wiki / Wikidot content, built with Tauri 2 + Vue 3 + Rust. It is NOT a generic rich text editor.

The bidirectional pipeline:
```
Wikitext ↔ ProseMirror JSON ↔ WYSIWYG Editor (TipTap/ProseMirror)
```

## Commands

### Frontend (Vue 3 + Vite)
```bash
npm install
npm run dev        # Dev server on port 5173
npm run build      # Type-check + build
```

### Tauri / Rust App
```bash
cd src-tauri && cargo tauri dev     # Run full desktop app
cd src-tauri && cargo tauri build   # Build for distribution
cd src-tauri && cargo check         # Type-check Rust
```

### Rust Tests (w_parser crate)
```bash
cd src-tauri && cargo test -p w_parser                         # Run all parser tests
cd src-tauri && cargo test -p w_parser <test_name> -- --exact  # Run a single test
```

### Code View Subproject (CodeMirror 6)
```bash
cd public/code_view && npm install
cd public/code_view && npm run build   # Regenerates Lezer parser from grammar
cd public/code_view && npm run dev     # Watch mode
cd public/code_view && npm run lint    # ESLint
```

## Architecture

### Layers

**1. Frontend UI (`src/`)**
- Entry: `src/main.ts` → `App.vue` → calls `connectIpc()` to wire up IPC
- Editor: `src/components/editor/EditorCanvas.vue` (TipTap instance)
- All TipTap extensions registered in `src/stores/editor/extensions.ts`; individual extensions in `src/stores/editor/extensions/`
- Editor instance singleton: `src/stores/editor/instance.ts` (`getEditor()` / `setEditor()`)
- Toolbar and context menu **components** are thin — they delegate to store helpers in `src/stores/btnToolBar/` and `src/stores/btnContextMenu/`; keep logic there, not in Vue components

**2. IPC Bridge (`src/ipc/`)**
- `src/ipc/ipc.ts` connects the CodeView and CodeExport extensions
- `src/ipc/Extensions/CodeView/` — manages the code view window and HTML→TipTap conversion
- `src/ipc/Extensions/CodeExport/` — exports ProseMirror JSON to Wikitext

**3. Code View Window (`public/code_view/`)**
- A separate browser window opened via Tauri command `open_code_view_window`
- Built independently from the main frontend; changes to it require `npm run build` in that directory
- Wikidot syntax grammar: `public/code_view/src/wikidot.grammar` (Lezer); `parser.js` is generated — do not edit it directly

**4. Tauri Shell (`src-tauri/src/`)**
- `main.rs` — Tauri entry point, registers all `#[tauri::command]` handlers
- Handlers in `src-tauri/src/handlers/`: `connect_parser.rs`, `connect_exporter.rs`, `open_code_view.rs`, `save.rs`, `insert_user_css.rs`

**5. Rust Parser Crate (`crates/w_parser/`)**
- Converts Wikidot Wikitext → HTML (wraps ftml v1.40.0)
- Pipeline: FTML preprocessing → include expansion (ResourcePack) → pre-tokenization interceptors → FTML tokenize/render → post-render interceptors
- Source text is written to `temp/origin.ftml` before parsing

**6. Rust Exporter Crate (`crates/ltmf/`)**
- Converts ProseMirror JSON → Wikidot Wikitext
- Pipeline: `preprocess()` → `interpret()` → `ftml_fmt()` → `merge_final_output()`
- Include architecture (strict module boundaries — do not merge):
  ```
  variable_loader.rs → SQLite mapping → search.rs → generator.rs
  ```
- SQL: always use `.sql` files; never inline SQL. Use `crates/ltmf/src/interpreter/include/variable_name_config_table.sql` directly in tests.

## Rules (from AGENTS.md)

1. **Do not redesign architecture** — no new frameworks, pipelines, or abstractions unless explicitly requested
2. **Export correctness is the highest priority** — preserve exporter behavior, include behavior, resource pack compatibility, and Wikitext output above all else
3. **No unnecessary dependencies** — check if functionality already exists before adding a crate/package
4. **Respect module boundaries** — especially in the include pipeline; do not merge responsibilities across files
5. **ProseMirror data is source of truth** — use node attrs, node content, `data-editor` metadata; avoid HTML parsing when structured data exists
6. **Keep solutions simple** — prefer functions/modules/enums/traits; avoid factory/provider/manager patterns
7. **Do not remove debugging information** — keep existing logs, assertions, and error messages unless explicitly asked
8. **When uncertain, stop and ask** — do not guess, silently change behavior, or invent exporter logic

## Conventions

- Import internal `.ts` files with explicit `.ts` extension
- Prettier is configured with `tabWidth: 4`
- ESLint is only configured in `public/code_view/`
- Custom TipTap extensions: one file per extension in `src/stores/editor/extensions/`, registered centrally in `src/stores/editor/extensions.ts`
- `wj-*` tag mappings and ARIA/ID attributes on custom nodes must be preserved for round-tripping
- Editor saves to `.txt` files containing raw Wikidot code
