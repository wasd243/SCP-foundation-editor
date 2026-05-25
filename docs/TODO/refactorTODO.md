## Refactor TODO

### In `crates\w_parser\src\lib.rs`
`DEFAULT_RESOURCEPACK_ROOT` is derived from `CARGO_MANIFEST_DIR` 
(a build-time path). In a bundled Tauri app this directory typically won’t exist, 
so resourcepack includes will fail outside a dev workspace. Consider resolving the 
resourcepack root at runtime (e.g., 
from Tauri’s resource/app data directory) and passing it into 
`render_wikidot_to_html_with_resourcepack` instead of hardcoding a compile-time path.
