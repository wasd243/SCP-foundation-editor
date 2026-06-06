use std::fs;

const ORIGIN_SOURCE_TEXT: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../crates/ltmf/cache/origin.ftml"
);

#[tauri::command]
pub fn parse_wikidot(source_text: String) -> Result<w_parser::FtmlParseOutput, String> {

    // cache the original source text to compare with the generated one
    fs::write(ORIGIN_SOURCE_TEXT, &source_text)
        .map_err(|err| format!("failed to cache original source text: {err}"))?;

    // let ftml parser parse the source text
    w_parser::render_wikidot_to_html(&source_text)
}
