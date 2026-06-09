mod handlers;

use handlers::{
    connect_exporter::export_code, connect_exporter::export_css, connect_parser::parse_wikidot,
    open_code_view::open_code_view_window, open_code_view::patch_get_user_css,
    open_code_view::read_final_output,
};

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            parse_wikidot,
            open_code_view_window,
            read_final_output,
            export_code,
            export_css,
            // patch functions here
            patch_get_user_css,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Tauri application");
}
