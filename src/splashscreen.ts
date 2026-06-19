import { invoke } from "@tauri-apps/api/core";

/**
 * Close the splashscreen and reveal the main window.
 *
 * Idempotent: the editor's `onCreate` and the startup fallback timer both call
 * this, but the backend command only runs once. Safe to call outside Tauri
 * (e.g. plain `npm run dev` in a browser) — the rejected invoke is swallowed.
 */
let closed = false;

export async function closeSplashscreen(): Promise<void> {
    if (closed) return;
    closed = true;

    try {
        await invoke("close_splashscreen");
    } catch (e) {
        console.warn("Could not close splashscreen:", e);
    }
}

/** Hard ceiling: never leave the user stuck on the splash. */
export const SPLASH_FALLBACK_MS = 20_000;
