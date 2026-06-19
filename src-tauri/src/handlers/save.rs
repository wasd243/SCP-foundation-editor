use crate::handlers::open_code_view::FINAL_OUTPUT_PATH;
use std::fs;
use std::path::Path;

/// Save the final output to a file.
#[tauri::command]
pub fn save_ftml(path: String, name: String) -> Result<(), String> {
    if path.is_empty() {
        return Err("Path cannot be empty.".into());
    }
    if name.is_empty() {
        return Err("Name cannot be empty.".into());
    }

    let save_path = Path::new(&path).join(&name);

    // Ensure the destination folder exists (e.g. the auto-save `saves\` dir).
    if let Some(parent) = save_path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    fs::copy(FINAL_OUTPUT_PATH, &save_path).map_err(|e| e.to_string())?;
    Ok(())
}

/// Hardcoded auto-save destination, anchored to the project root at build time.
/// `CARGO_MANIFEST_DIR` is `<root>/src-tauri`, so one `..` reaches the repo root.
const AUTO_SAVE_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../saves/autosave.ftml");

/// Auto-save the final output to the fixed `saves/autosave.ftml` file.
///
/// Reads the latest exporter output and writes it to the hardcoded path,
/// overwriting on every tick. The `saves` folder is created if missing.
#[tauri::command]
pub fn auto_save_ftml() -> Result<(), String> {
    if let Some(parent) = Path::new(AUTO_SAVE_PATH).parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    let content = fs::read_to_string(FINAL_OUTPUT_PATH).map_err(|e| e.to_string())?;
    fs::write(AUTO_SAVE_PATH, content).map_err(|e| e.to_string())?;
    Ok(())
}

/// Read the auto-saved Wikitext from the fixed `saves/autosave.ftml` file.
///
/// Returns the raw source so the frontend can feed it back into the parser,
/// the same way opening a file does.
#[tauri::command]
pub fn read_autosave_ftml() -> Result<String, String> {
    if !Path::new(AUTO_SAVE_PATH).exists() {
        return Err("No auto-save file found yet.".into());
    }

    fs::read_to_string(AUTO_SAVE_PATH).map_err(|e| e.to_string())
}
