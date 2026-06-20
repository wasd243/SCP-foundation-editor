use ltmf::ftml_fmt::user_css_path;
use std::fs;

/// This function saves the user css to the cache: `temp/user_css.css`.
#[tauri::command]
pub fn save_user_css_to_cache(css: String) -> Result<(), String> {
    fs::write(user_css_path(), css).map_err(|e| e.to_string())?;
    Ok(())
}
