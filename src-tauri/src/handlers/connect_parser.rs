use crate::utils::path::temp_dir;
use std::fs;

#[tauri::command]
pub fn parse_wikidot(source_text: String) -> Result<w_parser::FtmlParseOutput, String> {
    // temp the original source text to compare with the generated one
    let cache_dir = temp_dir();
    fs::create_dir_all(&cache_dir)
        .map_err(|err| format!("failed to create temp directory: {err}"))?;
    fs::write(cache_dir.join("origin.ftml"), &source_text)
        .map_err(|err| format!("failed to temp original source text: {err}"))?;

    // let ftml parser parse the source text
    w_parser::render_wikidot_to_html(&source_text)
}
