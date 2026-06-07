use std::fs;

const ORIGIN_SOURCE_TEXT: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../temp/origin.ftml"
);
const CACHE_DIR: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../temp");

#[tauri::command]
pub fn parse_wikidot(source_text: String) -> Result<w_parser::FtmlParseOutput, String> {

    // temp the original source text to compare with the generated one
    fs::create_dir_all(CACHE_DIR)
        .map_err(|err| format!("failed to create temp directory: {err}"))?;
    fs::write(ORIGIN_SOURCE_TEXT, &source_text)
        .map_err(|err| format!("failed to temp original source text: {err}"))?;

    // let ftml parser parse the source text
    w_parser::render_wikidot_to_html(&source_text)
}
