# Contributing

All contributions are welcome — bug fixes, new Wikidot node support, exporter improvements, UI changes, and documentation. This guide will help you get set up and submit a PR that lands cleanly.

---

## Dev Setup

### Option A — Docker (recommended)

A `Dockerfile` is included at the repo root with all system dependencies pre-installed (Rust stable, Node 22 LTS, Tauri CLI, and the required GTK/WebKit libraries).

```bash
docker build -t scp-wysiwyg .
docker run -it --rm -v $(pwd):/app scp-wysiwyg bash
```

Inside the container, proceed with the native commands below.

### Option B — Native

You'll need:
- **Rust** (stable toolchain via [rustup](https://rustup.rs))
- **Node.js** 22 LTS
- **Tauri CLI v2**: `cargo install tauri-cli --version "^2" --locked`
- Linux system libraries listed in the `Dockerfile` (GTK 3, WebKit2GTK 4.1, libsoup 3, etc.)

---

## Build & Test Commands

### Frontend (Vue 3 + Vite)
```bash
npm install
npm run dev        # Dev server on port 5173
npm run build      # Build
```

### Tauri Desktop App
```bash
cargo tauri dev     # Run full desktop app
cargo tauri build   # Build for distribution
cargo check
```

### Rust Parser Tests (`w_parser`)
```bash
cd crates/w_parser/ && cargo test
```

### Rust Exporter Tests (`ltmf`)
```bash
cd crates/ltmf/ && cargo test 
```

### Code View Subproject (CodeMirror 6)
```bash
cd public/code_view && npm install
cd public/code_view && node build      # Regenerates Lezer parser from grammar
```

---

## Submitting a PR

1. Fork the repo and create a branch from `main`.
2. Use a descriptive branch name with one of these prefixes:
   - `feat/` — new feature or Wikidot node support
   - `fix/` — bug fix
   - `docs/` — documentation only
   - `chore/` — tooling, deps, CI 
   - etc.
3. Open a PR against `main` and fill out the PR template.

---

## Areas That Need Extra Care

The following parts of the codebase are fragile. If your PR touches any of them, explain in the PR description why the change is necessary and how you verified it.


### Exporter pipeline (`crates/ltmf/`)
Export correctness is the **highest priority** in this project. Any change that affects Wikidot output — even whitespace — can break round-tripping for real wiki pages. Test your change against a variety of Wikidot syntax and include the input/output in your PR description.

### Include pipeline module boundaries
Resourcepack `[[include]]` pipeline modules are abandoned due to their macro-like, non-reversible nature. See the full explanation in [Include_block.md](./docs/Include_block.md).

### `wj-*` attribute round-tripping
FTML parser output node extensions use `wj-*` tag mappings and ARIA/ID attributes to preserve structure across the Wikitext ↔ ProseMirror ↔ HTML pipeline. Changes to these attributes can silently break round-tripping. If your PR touches any custom node extension, verify that the node serializes and deserializes correctly end-to-end.

---

## General Rules

- **Keep logs and error messages** — do not remove existing debugging output unless a change explicitly requires it.
- **ProseMirror node data is the source of truth** — use node attrs, node content, and `data-editor` metadata. Avoid reconstructing state from rendered HTML.

---

This is a personal project developed primarily for the SCP-CN community.
While contributions are welcome, the project is still in early stages.