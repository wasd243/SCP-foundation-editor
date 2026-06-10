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

    fs::copy(FINAL_OUTPUT_PATH, &save_path).map_err(|e| e.to_string())?;
    Ok(())
}
