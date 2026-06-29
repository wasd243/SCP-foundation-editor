//! Runtime temp/cache directory for the parser, resolved per-user.

use directories::ProjectDirs;
use std::fs;
use std::path::PathBuf;

fn project() -> ProjectDirs {
    ProjectDirs::from("com", "wasd243", "scpwysiwyg").expect("no valid home directory")
}

/// Runtime temp/cache directory. Created if missing.
pub fn temp_dir() -> PathBuf {
    let dir = project().cache_dir().join("temp");
    fs::create_dir_all(&dir).unwrap();
    dir
}

/// Runtime resourcepack root (`data_dir()/resourcepack`).
///
/// The host app (src-tauri) copies the bundled resourcepack here at startup;
/// w_parser cannot depend on Tauri, so it resolves the same per-user path via
/// `directories`, mirroring [`temp_dir`]. Missing files (e.g. unset before a
/// copy, or in tests) degrade to the includer's no_such_include behavior.
pub fn resourcepack_dir() -> PathBuf {
    project().data_dir().join("resourcepack")
}

/// Persistent ignored-lines settings file (`config_dir()/ignore_lines.json`),
/// written by the host. w_parser reads it directly as the single source of truth.
fn ignore_lines_file_path() -> PathBuf {
    project().config_dir().join("ignore_lines.json")
}

/// Read the saved ignored-line tokens (e.g. `["1-10", "15"]`). A missing,
/// unreadable, or malformed file all map to an empty list. Never panics.
pub fn read_ignore_lines() -> Vec<String> {
    let Ok(contents) = fs::read_to_string(ignore_lines_file_path()) else {
        return Vec::new();
    };
    let Ok(value) = serde_json::from_str::<serde_json::Value>(&contents) else {
        return Vec::new();
    };
    value
        .get("ignore_lines")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(str::to_string))
                .collect()
        })
        .unwrap_or_default()
}

/// Test-only: materialize the dev-tree resourcepack into [`resourcepack_dir`]
/// so unit tests that read include/theme files find them, mirroring the host's
/// startup copy. This is a compile-time *test* fixture, never used at runtime.
#[cfg(test)]
pub(crate) fn ensure_test_resourcepack() {
    let source = PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack"));
    copy_dir_if_missing(&source, &resourcepack_dir());
}

#[cfg(test)]
fn copy_dir_if_missing(source: &std::path::Path, dest: &std::path::Path) {
    let _ = fs::create_dir_all(dest);
    let Ok(entries) = fs::read_dir(source) else {
        return;
    };
    for entry in entries.flatten() {
        let from = entry.path();
        let to = dest.join(entry.file_name());
        if from.is_dir() {
            copy_dir_if_missing(&from, &to);
        } else if !to.exists() {
            let _ = fs::copy(&from, &to);
        }
    }
}
