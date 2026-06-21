use crate::handlers::open_code_view::final_output_path;
use crate::utils::path::saves_dir;
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

    fs::copy(final_output_path(), &save_path).map_err(|e| e.to_string())?;
    Ok(())
}

/// Auto-save the final output to the fixed `saves/autosave.ftml` file.
///
/// Reads the latest exporter output and writes it to the runtime saves dir,
/// overwriting on every tick. The `saves` folder is created if missing.
#[tauri::command]
pub fn auto_save_ftml() -> Result<(), String> {
    let auto_save_path = saves_dir().join("autosave.ftml");
    if let Some(parent) = auto_save_path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    let content = fs::read_to_string(final_output_path()).map_err(|e| e.to_string())?;
    fs::write(&auto_save_path, content).map_err(|e| e.to_string())?;
    Ok(())
}

/// Read the auto-saved Wikitext from the fixed `saves/autosave.ftml` file.
///
/// Returns the raw source so the frontend can feed it back into the parser,
/// the same way opening a file does.
#[tauri::command]
pub fn read_autosave_ftml() -> Result<String, String> {
    let auto_save_path = saves_dir().join("autosave.ftml");
    if !auto_save_path.exists() {
        return Err("No auto-save file found yet.".into());
    }

    fs::read_to_string(&auto_save_path).map_err(|e| e.to_string())
}
