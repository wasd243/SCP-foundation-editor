#[tauri::command]
pub fn get_theme() -> String {
    w_parser::get_theme_css()
}
