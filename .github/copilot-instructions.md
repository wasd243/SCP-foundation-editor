# Copilot Instructions for SCP Foundation Editor

## Build, test, and lint commands

### Root frontend (Vue 3 + TipTap)
- Install deps: `npm install`
- Dev server: `npm run dev`
- Build (includes type-check): `npm run build`
- Preview built app: `npm run preview`

### Tauri shell + Rust backend
- Run Tauri app in dev mode: `cd src-tauri && cargo tauri dev`
- Build Tauri app: `cd src-tauri && cargo tauri build`
- Check the Rust backend crate: `cd src-tauri && cargo check`

### Rust parser crate (`w_parser`)
- Run all tests: `cd src-tauri && cargo test -p w_parser`
- Run a single test by name: `cd src-tauri && cargo test -p w_parser <test_name> -- --exact`

### Code View subproject (`public/code_view`)
- Install deps: `cd public/code_view && npm install`
- Build CodeMirror bundle: `cd public/code_view && npm run build`
- Lint JS files: `cd public/code_view && npm run lint`

## High-level architecture
- The app is a **Tauri host (`src-tauri`) plus a Vue 3 frontend (`src`)**. Frontend startup happens in `src/main.ts`, which mounts `App.vue` and initializes IPC through `connectIpc()`.
- The editor canvas is a **TipTap editor** in `src/components/editor/EditorCanvas.vue`. Its extensions are assembled centrally in `src/stores/editor/extensions.ts`.
- Editor access is centralized in `src/stores/editor/instance.ts`; toolbar and context-menu components stay thin and call store helpers under `src/stores/btnToolBar/*` and `src/stores/btnContextMenu/*`.
- **Code View** is a separate CodeMirror-based editor under `public/code_view`, opened by the Tauri command `open_code_view_window`. It posts changes back to the main window, which calls `parse_wikidot`, then Rust `w_parser` converts Wikidot to HTML/AST, and DOM adapters in `src/ipc/Extensions/CodeView/htmlAdapter/*` reshape output before it goes back into TipTap.
- The Rust side is split between the Tauri shell in `src-tauri`, the parser crate `crates/w_parser`, and the exporter crate `crates/ltmf`. The parser command temporarily writes source text to `temp/origin.ftml` before rendering.

## Key conventions
- Use explicit `.ts` import suffixes in internal TypeScript imports.
- Keep editor actions in store helper modules, not in Vue button components.
- Prefer ProseMirror node attrs, node content, and `data-editor` metadata over reconstructing state from rendered HTML.
- Preserve `wj-*` tag mappings and ARIA/ID attributes for round-tripping custom nodes.
- When parser output is not TipTap-compatible, adapt it in the Code View `htmlAdapter` replacers instead of changing the parser pipeline.
- Do not hardcode SQL inline; use the existing `.sql` files, especially `crates/ltmf/src/interpreter/include/variable_name_config_table.sql` for include-related work.
- Preserve existing logs, assertions, and error messages unless a change explicitly requires otherwise.
- Keep IPC wiring in `src/main.ts` via `connectIpc()`, and add new cross-window/event integrations under `src/ipc`.
- Optimize for export correctness and Wikidot fidelity over refactoring or abstraction.
