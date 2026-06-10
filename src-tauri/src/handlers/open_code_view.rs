use std::fs;

pub(crate) const FINAL_OUTPUT_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../temp/final_output.ftml");

/// Open the code view window.
#[tauri::command]
pub fn open_code_view_window() -> &'static str {
    "code_view/index.html"
}

/// Read the final output file from the temp directory.
#[tauri::command]
pub fn read_final_output() -> Result<String, String> {
    fs::read_to_string(FINAL_OUTPUT_PATH)
        .map_err(|e| format!("Failed to read {}: {}", FINAL_OUTPUT_PATH, e))
}

/// This patch function is used to solve the problem of the user CSS not being loaded by parser.
/// I don't know why parser has blocked the user CSS, so do not remove this unless you fix the CSS blocking issue.
#[tauri::command]
pub fn patch_get_user_css() -> String {
    const CSS_CACHE_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../temp/user_css.css");
    fs::read_to_string(CSS_CACHE_PATH).unwrap_or_default()
}
