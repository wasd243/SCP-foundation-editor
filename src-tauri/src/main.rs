#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod handlers;
pub mod utils;

use handlers::{
    connect_exporter::export_code,
    connect_exporter::export_css,
    connect_parser::parse_wikidot,
    insert_user_css::save_user_css_to_cache,
    log_and_write_json::log_and_write_json,
    module_rate::{read_module_rate_temp, rewrite_module_rate_temp},
    open_code_view::open_code_view_window,
    open_code_view::patch_get_user_css,
    open_code_view::read_final_output,
    save::auto_save_ftml,
    save::read_autosave_ftml,
    save::save_ftml,
    settings::get_saves_path,
    settings::open_saves_dir,
    settings::reset_saves_path,
    settings::set_saves_path,
    splashscreen::close_splashscreen,
};

use tauri::{Builder, Manager};

fn main() {
    env_logger::init();
    Builder::default()
        .setup(|app| {
            // The resourcepack ships as a bundled Tauri resource (see
            // tauri.conf.json `bundle.resources`). Copy it from the read-only
            // install location into the per-user resourcepack dir at startup so
            // the parser/exporter crates — which cannot depend on Tauri — can
            // resolve the same path via `directories`.
            let bundled = app.path().resource_dir()?.join("resourcepack");
            let dest = utils::path::resourcepack_dir();
            if let Err(error) = utils::path::copy_dir_overwrite(&bundled, &dest) {
                log::warn!(
                    "failed to copy bundled resourcepack from {} to {}: {error}",
                    bundled.display(),
                    dest.display()
                );
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            parse_wikidot,
            open_code_view_window,
            read_final_output,
            export_code,
            export_css,
            save_ftml,
            auto_save_ftml,
            read_autosave_ftml,
            get_saves_path,
            set_saves_path,
            reset_saves_path,
            open_saves_dir,
            save_user_css_to_cache,
            read_module_rate_temp,
            rewrite_module_rate_temp,
            close_splashscreen,
            log_and_write_json,
            // patch functions here
            patch_get_user_css,
        ])
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .run(tauri::generate_context!())
        .expect("failed to run Tauri application");
}
