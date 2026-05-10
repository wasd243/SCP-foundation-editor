mod handlers;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            handlers::connect_parser::parse_wikidot,
            handlers::open_code_view::open_code_view_window
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Tauri application");
}
