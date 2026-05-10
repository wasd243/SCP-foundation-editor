// open_code_view.rs
// Allow tauri to open a new Code View window

use tauri::{AppHandle, WebviewWindowBuilder, WebviewUrl};

#[tauri::command]
pub fn open_code_view_window(app: AppHandle) -> Result<(), String> {
    WebviewWindowBuilder::new(
        &app,
        "code-view",
        WebviewUrl::App("code_view/index.html".into()),
    )
        .title("Code View")
        .inner_size(1000.0, 700.0)
        .build()
        .map_err(|err| err.to_string())?;

    println!("Code View window opened");
    Ok(())
}
