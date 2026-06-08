use std::fs;

const FINAL_OUTPUT_PATH: &str =
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
