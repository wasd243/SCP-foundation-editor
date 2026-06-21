//! Runtime path resolution for the desktop app, resolved per-user.

use directories::ProjectDirs;
use serde_json::{Value, json};
use std::fs;
use std::path::{Path, PathBuf};

fn project() -> ProjectDirs {
    ProjectDirs::from("com", "wasd243", "scpwysiwyg").expect("no valid home directory")
}

/// Runtime temp/cache directory for the Tauri handlers. Created if missing.
pub fn temp_dir() -> PathBuf {
    let dir = project().cache_dir().join("temp");
    fs::create_dir_all(&dir).unwrap();
    dir
}

/// Fixed location of the settings file. This is NEVER user-configurable — the
/// user's chosen saves path is stored *inside* it, but the file itself always
/// lives under `config_dir()` to avoid a resolution recursion.
fn config_file_path() -> PathBuf {
    project().config_dir().join("settings.json")
}

/// The built-in default saves directory (`data_dir()/saves`).
fn default_saves_dir() -> PathBuf {
    project().data_dir().join("saves")
}

/// Read the user's custom saves path from the settings file, if any.
///
/// Missing file, unreadable file, parse error, or an empty value all map to
/// `None` (i.e. "use the default"). Never panics.
pub fn read_saves_setting() -> Option<String> {
    let contents = fs::read_to_string(config_file_path()).ok()?;
    let value: Value = serde_json::from_str(&contents).ok()?;
    let path = value.get("saves_path")?.as_str()?.trim();
    if path.is_empty() {
        None
    } else {
        Some(path.to_string())
    }
}

/// Persist the user's saves path into the settings file. `None` clears the
/// custom path (reverting to the default). Creates `config_dir()` if missing.
pub fn write_saves_setting(path: Option<&str>) -> Result<(), String> {
    let file = config_file_path();
    if let Some(parent) = file.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    let contents =
        serde_json::to_string_pretty(&json!({ "saves_path": path })).map_err(|e| e.to_string())?;
    fs::write(&file, contents).map_err(|e| e.to_string())
}

/// Validate that `dir` can be created and written to. Creates the directory if
/// needed and writes/removes a probe file. Returns a clear error string on
/// failure (e.g. read-only or removed/unplugged location). Never panics.
pub fn validate_writable(dir: &Path) -> Result<(), String> {
    fs::create_dir_all(dir).map_err(|e| format!("Cannot create directory: {e}"))?;

    let probe = dir.join(".scpwysiwyg_write_test");
    fs::write(&probe, b"test").map_err(|e| format!("Directory is not writable: {e}"))?;
    let _ = fs::remove_file(&probe);

    Ok(())
}

/// Runtime saves directory for the Tauri handlers.
///
/// Resolution: if the user has set a custom path AND it is writable, use it;
/// otherwise fall back to the default `data_dir()/saves`. Never panics — a bad
/// or removed custom path silently degrades to the default.
pub fn saves_dir() -> PathBuf {
    if let Some(custom) = read_saves_setting() {
        let path = PathBuf::from(&custom);
        if validate_writable(&path).is_ok() {
            return path;
        }
    }

    let dir = default_saves_dir();
    // Best-effort create; callers that write also create_dir_all the parent
    // with proper error handling, so a failure here must not abort.
    let _ = fs::create_dir_all(&dir);
    dir
}

/// Per-user resourcepack root (`data_dir()/resourcepack`).
///
/// This is where the bundled resourcepack is materialized at startup so the
/// parser/exporter crates (which cannot depend on Tauri) can resolve the same
/// path via `directories`. Mirrors `w_parser::resourcepack_dir` /
/// `ltmf::resourcepack_dir`.
pub fn resourcepack_dir() -> PathBuf {
    project().data_dir().join("resourcepack")
}

/// Recursively copy `source` into `dest`, overwriting existing files. Best-effort
/// per entry: a single failure is reported but does not abort the remaining
/// copies. Used to materialize the bundled resourcepack into [`resourcepack_dir`].
pub fn copy_dir_overwrite(source: &Path, dest: &Path) -> std::io::Result<()> {
    fs::create_dir_all(dest)?;
    for entry in fs::read_dir(source)? {
        let entry = entry?;
        let from = entry.path();
        let to = dest.join(entry.file_name());
        if from.is_dir() {
            copy_dir_overwrite(&from, &to)?;
        } else {
            fs::copy(&from, &to)?;
        }
    }
    Ok(())
}
