#[tauri::command]
pub fn open_code_view_window() -> &'static str {
    "code_view/index.html"
}
