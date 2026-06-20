//! Runtime path resolution for the parser's temp/cache directory.
//!
//! `src-tauri` resolves the real per-user cache dir at startup (via Tauri) and
//! pushes it in with [`set_temp_dir`]. When unset — e.g. under `cargo test` or
//! any standalone use of this crate — [`temp_dir`] falls back to the repo
//! `temp/` directory so existing behavior is preserved.

use std::path::PathBuf;
use std::sync::OnceLock;

static TEMP_DIR: OnceLock<PathBuf> = OnceLock::new();

/// Set the runtime temp/cache directory. Intended to be called once by the host
/// application at startup; subsequent calls are ignored.
pub fn set_temp_dir(dir: impl Into<PathBuf>) {
    let _ = TEMP_DIR.set(dir.into());
}

/// Runtime temp/cache directory.
///
/// Returns the dir set via [`set_temp_dir`], or the repo `temp/` directory
/// (anchored to `CARGO_MANIFEST_DIR` at build time) when unset.
pub fn temp_dir() -> PathBuf {
    TEMP_DIR
        .get()
        .cloned()
        .unwrap_or_else(|| PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp")))
}
