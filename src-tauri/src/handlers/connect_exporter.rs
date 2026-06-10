use ltmf::export_wikitext;

/// This function is used to export the ProseMirror JSON to wikitext, based on `ltmf` library.
///
/// `ltmf` Directory:
/// `crates\ltmf\`
#[tauri::command]
pub fn export_code(json: String) -> Result<String, String> {
    // println!("{json}");
    export_wikitext(&json)
}

// This function is used to check editor CSS, debug only.
#[tauri::command]
pub fn export_css(css: String) {
    println!("{css}");
}
