// The exporter library is not implemented yet.
// This is only a placeholder.

// #[tauri::command]
// pub fn export_wikitext(wikitext: &str) -> String {
//     ltmf::export_wikitext(&wikitext)
// }
// 
// #[tauri::command]
// pub fn export_patch(patch: &str) -> String{
//     ltmf::export_patch(&patch)
// }

#[tauri::command]
pub fn export_json(json: String) {
    println!("{json}")
}
