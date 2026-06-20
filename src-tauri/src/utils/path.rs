//! Runtime path resolution for the desktop app, resolved per-user.

use directories::ProjectDirs;
use std::path::PathBuf;

fn project() -> ProjectDirs {
    ProjectDirs::from("com", "wasd243", "scpwysiwyg").expect("no valid home directory")
}

/// Runtime temp/cache directory for the Tauri handlers. Created if missing.
pub fn temp_dir() -> PathBuf {
    let dir = project().cache_dir().join("temp");
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// Runtime saves directory for the Tauri handlers. Created if missing.
pub fn saves_dir() -> PathBuf {
    let dir = project().data_dir().join("saves");
    std::fs::create_dir_all(&dir).unwrap();
    dir
}
