# Copilot Instructions for SCP Foundation Editor

## Build, test, and lint commands

### Root frontend (Vue 3 + TipTap)

- Install deps: `npm install`
- Dev server: `npm run dev`
- Build (includes type-check): `npm run build`
- Preview built app: `npm run preview`

### Tauri shell + Rust parser bridge

- Run Tauri app in dev mode (from `src-tauri/`): `cargo tauri dev`
- Build Tauri app (from `src-tauri/`): `cargo tauri build`
- Build/check Rust backend crate only (from `src-tauri/`): `cargo check`

### Rust parser crate (`w_parser`)

- Run all tests (from `src-tauri/`): `cargo test -p w_parser`
- Run a single test by name (from `src-tauri/`): `cargo test -p w_parser <test_name> -- --exact`

### Code View subproject (`public/code_view`)

- Install deps: `cd public/code_view && npm install`
- Build CodeMirror bundle: `cd public/code_view && npm run build`
- Lint JS files: `cd public/code_view && npm run lint`

## High-level architecture

- The desktop app is a **Tauri host (`src-tauri`) + Vue frontend (`src`)**. Tauri exposes commands and the Vue app calls them through `@tauri-apps/api/core` `invoke`.
- The editor canvas is a **TipTap editor** (`src/components/editor/EditorCanvas.vue`) with extensions assembled in `src/stores/editor/extensions.ts`.
- Editor instance access is centralized through a shared singleton (`src/stores/editor/instance.ts`), and toolbar/context-menu actions call it through small store helpers in `src/stores/btnToolBar/*` and `src/stores/btnContextMenu/*`.
- Code View is a separate web editor loaded in an iframe from `public/code_view/index.html`, opened by Tauri command `open_code_view_window`.
- Sync flow:
  1. `public/code_view` posts `window.parent.postMessage({ type: "code-view-content-changed", payload })`.
  2. Frontend listener (`src/ipc/Extensions/CodeView/SyncToParser.ts`) calls Tauri command `parse_wikidot`.
  3. Rust command (`src-tauri/src/handlers/connect_parser.rs`) calls `w_parser::render_wikidot_to_html_and_ast`.
  4. Returned HTML is transformed by DOM adapters (`src/ipc/Extensions/CodeView/htmlAdapter/*`) and then injected back into TipTap via `code-view-parser-html` custom event.
- The Rust parser crate (`crates/w_parser`) wraps FTML parsing/rendering and includes an interceptor layer (`ftml_interceptor`) for Wikidot constructs that need preprocessing before FTML tokenization (currently `[[module rate]]` handling).

## Key conventions in this repository

- **Use explicit `.ts` import suffixes** in internal TypeScript imports (enabled by `allowImportingTsExtensions` in `tsconfig.json`).
- **Keep editor commands in store helper modules**, not in Vue button components. Components emit UI events; store helpers execute TipTap commands via `getEditor()`.
- **Custom TipTap nodes map to `wj-*` HTML tags** (for example tabview nodes in `TabViewE.ts`) and preserve ARIA/ID attributes for round-tripping.
- **When Code View parser output is not directly TipTap-compatible, adapt it in `htmlAdapter` replacers** before inserting into the editor.
- **IPC wiring is initialized from `src/main.ts` via `connectIpc()`**, so new cross-window/event integrations should be attached under `src/ipc`.
