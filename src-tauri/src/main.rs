mod handlers;

use handlers::{
    connect_parser::parse_wikidot,
    open_code_view::open_code_view_window,
    connect_exporter::export_json,
    connect_exporter::export_css,
};

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            parse_wikidot,
            open_code_view_window,
            export_json,
            export_css
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Tauri application");
}
