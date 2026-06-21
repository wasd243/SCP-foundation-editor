use std::sync::atomic::{AtomicBool, Ordering};
use tauri::{Manager, Window};

/// Authoritative "already closing" guard. The splash auto-close timer, the
/// splash click, and the main-window fallback can all call this command; the
/// first one wins and the rest are no-ops, so the close path runs exactly once.
static SPLASH_DISMISSED: AtomicBool = AtomicBool::new(false);

/// Close the splashscreen window and reveal the main window.
///
/// Called by the frontend once the editor is truly ready (or by a fallback
/// timer), so the user never sees the blank WebView while Vue boots.
#[tauri::command]
pub async fn close_splashscreen(window: Window) -> Result<(), String> {
    // Run the close path exactly once, even if click and timer race.
    if SPLASH_DISMISSED.swap(true, Ordering::SeqCst) {
        return Ok(());
    }

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
