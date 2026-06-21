//! Tauri commands for the user-configurable saves directory.
//!
//! The saves path is the only configurable location; the settings file that
//! stores it always lives at the fixed `config_dir()` (see `utils::path`).

use crate::utils::path::{saves_dir, validate_writable, write_saves_setting};
use std::path::{Path, PathBuf};

/// Return the currently resolved saves directory as a display string, so the
/// frontend can show the user exactly where their data goes.
#[tauri::command]
pub fn get_saves_path() -> Result<String, String> {
    Ok(saves_dir().to_string_lossy().to_string())
}

/// Set a custom saves directory. Validates the path is writable *before*
/// persisting it; on failure returns a clear error and changes nothing.
#[tauri::command]
pub fn set_saves_path(path: String) -> Result<(), String> {
    if path.trim().is_empty() {
        return Err("Path cannot be empty.".into());
    }

    validate_writable(&PathBuf::from(&path))?;
    write_saves_setting(Some(&path))
}

/// Clear the custom saves path, reverting to the default `data_dir()/saves`.
#[tauri::command]
pub fn reset_saves_path() -> Result<(), String> {
    write_saves_setting(None)
}

/// Open the resolved saves directory in the OS file manager.
#[tauri::command]
pub fn open_saves_dir() -> Result<(), String> {
    let dir = saves_dir();
    open_in_file_manager(&dir)
}

fn open_in_file_manager(dir: &Path) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    let mut command = {
        let mut c = std::process::Command::new("explorer");
        c.arg(dir);
        c
    };

    #[cfg(target_os = "macos")]
    let mut command = {
        let mut c = std::process::Command::new("open");
        c.arg(dir);
        c
    };

    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    let mut command = {
        let mut c = std::process::Command::new("xdg-open");
        c.arg(dir);
        c
    };

    command
        .spawn()
        .map(|_| ())
        .map_err(|e| format!("Failed to open folder: {e}"))
}
