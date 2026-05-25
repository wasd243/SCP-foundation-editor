#[tauri::command]
pub fn parse_wikidot(source_text: String) -> Result<w_parser::FtmlParseOutput, String> {
    w_parser::render_wikidot_to_html(&source_text)
}
