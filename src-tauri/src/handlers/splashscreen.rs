use tauri::{Manager, Window};

/// Close the splashscreen window and reveal the main window.
///
/// Called by the frontend once the editor is truly ready (or by a fallback
/// timer), so the user never sees the blank WebView while Vue boots.
#[tauri::command]
pub async fn close_splashscreen(window: Window) -> Result<(), String> {
    // Close the splash if it is still around (idempotent on the frontend side).
    if let Some(splashscreen) = window.get_webview_window("splashscreen") {
        splashscreen.close().map_err(|e| e.to_string())?;
    }

    // Reveal the main window, which starts hidden in tauri.conf.json.
    if let Some(main) = window.get_webview_window("main") {
        main.show().map_err(|e| e.to_string())?;
        let _ = main.set_focus();
    }

    Ok(())
}
