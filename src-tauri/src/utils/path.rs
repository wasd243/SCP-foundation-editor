//! Runtime path resolution for the desktop app.
//!
//! In development the parser/exporter crates and the Tauri handlers anchor their
//! temp/cache and saves directories to the repo root via `CARGO_MANIFEST_DIR`.
//! That path does not exist on an end-user machine, so at startup [`init`]
//! resolves writable per-user directories (via Tauri) and:
//!
//! - records them here for the Tauri handlers ([`temp_dir`] / [`saves_dir`]);
//! - pushes the temp dir into the `ltmf` and `w_parser` crates, which keep their
//!   own [`OnceLock`] mirrors (they cannot depend on Tauri or on this crate).
//!
//! When [`init`] has not run (e.g. unit tests), the getters fall back to the
//! repo `temp/` and `saves/` directories so existing behavior is preserved.

use std::path::PathBuf;
use std::sync::OnceLock;

use tauri::{AppHandle, Manager};

static TEMP_DIR: OnceLock<PathBuf> = OnceLock::new();
static SAVES_DIR: OnceLock<PathBuf> = OnceLock::new();

/// Resolve the per-user runtime directories, create them, and push the temp dir
/// into the parser/exporter crates. Call once during Tauri `setup`.
pub fn init(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let temp = app.path().app_cache_dir()?.join("temp");
    let saves = app.path().app_data_dir()?.join("saves");

    std::fs::create_dir_all(&temp)?;
    std::fs::create_dir_all(&saves)?;

    // The crates can't see this module, so hand them the resolved temp dir.
    ltmf::set_temp_dir(temp.clone());
    w_parser::set_temp_dir(temp.clone());

    let _ = TEMP_DIR.set(temp);
    let _ = SAVES_DIR.set(saves);
    Ok(())
}

/// Runtime temp/cache directory for the Tauri handlers.
///
/// Returns the dir resolved by [`init`], or the repo `temp/` directory
/// (anchored to `CARGO_MANIFEST_DIR` at build time) when [`init`] has not run.
pub fn temp_dir() -> PathBuf {
    TEMP_DIR
        .get()
        .cloned()
        .unwrap_or_else(|| PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../temp")))
}

/// Runtime saves directory for the Tauri handlers.
///
/// Returns the dir resolved by [`init`], or the repo `saves/` directory
/// (anchored to `CARGO_MANIFEST_DIR` at build time) when [`init`] has not run.
pub fn saves_dir() -> PathBuf {
    SAVES_DIR
        .get()
        .cloned()
        .unwrap_or_else(|| PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../saves")))
}
