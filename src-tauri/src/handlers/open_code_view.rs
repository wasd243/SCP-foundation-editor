use crate::utils::path::temp_dir;
use std::fs;
use std::path::PathBuf;

/// Path to the exporter's final output file in the temp directory.
pub(crate) fn final_output_path() -> PathBuf {
    temp_dir().join("final_output.ftml")
}

/// Open the code view window.
#[tauri::command]
pub fn open_code_view_window() -> &'static str {
    "code_view/index.html"
}

/// Read the final output file from the temp directory.
#[tauri::command]
pub fn read_final_output() -> Result<String, String> {
    let path = final_output_path();
    fs::read_to_string(&path).map_err(|e| format!("Failed to read {}: {}", path.display(), e))
}

/// This patch function is used to solve the problem of the user CSS not being loaded by parser.
/// I don't know why parser has blocked the user CSS, so do not remove this unless you fix the CSS blocking issue.
#[tauri::command]
pub fn patch_get_user_css() -> String {
    fs::read_to_string(temp_dir().join("user_css.css")).unwrap_or_default()
}
