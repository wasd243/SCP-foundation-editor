mod handlers;

use handlers::{
    connect_exporter::export_code, connect_exporter::export_css, connect_parser::parse_wikidot,
    module_rate::read_module_rate_temp,
    open_code_view::open_code_view_window, open_code_view::patch_get_user_css,
    open_code_view::read_final_output, save::save_ftml, insert_user_css::save_user_css_to_cache,
};

use tauri::Builder;

fn main() {
    Builder::default()
        .invoke_handler(tauri::generate_handler![
            parse_wikidot,
            open_code_view_window,
            read_final_output,
            export_code,
            export_css,
            save_ftml,
            save_user_css_to_cache,
            read_module_rate_temp,
            // patch functions here
            patch_get_user_css,
        ])
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .run(tauri::generate_context!())
        .expect("failed to run Tauri application");
}
