use ltmf::export_wikitext;

#[tauri::command]
pub fn export_code(json: String) -> Result<String, String> {
    println!("{json}");
    
    export_wikitext(&json)
}

#[tauri::command]
pub fn export_css(css: String) {
    println!("{css}");
}
