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
/// ltmf cannot depend on Tauri, so it resolves the same per-user path via
/// `directories`, mirroring [`temp_dir`]. Missing files (e.g. unset before a
/// copy, or in tests) degrade to loading no include variables.
pub fn resourcepack_dir() -> PathBuf {
    project().data_dir().join("resourcepack")
}

/// Test-only: materialize the dev-tree resourcepack into [`resourcepack_dir`]
/// so unit tests that read include files find them, mirroring the host's
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
