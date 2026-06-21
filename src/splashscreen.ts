import { invoke } from "@tauri-apps/api/core";
import { emit } from "@tauri-apps/api/event";

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

/**
 * Tell the splashscreen that the main window's content is ready.
 *
 * The splash listens for this `main-ready` event and starts its own 5s
 * auto-close countdown from this moment, so the timer is anchored to actual
 * readiness rather than to when the splash first appeared. Fires once; safe to
 * call outside Tauri (the rejected emit is swallowed).
 */
let signalled = false;

export async function signalMainReady(): Promise<void> {
    if (signalled) return;
    signalled = true;

    try {
        await emit("main-ready");
    } catch (e) {
        console.warn("Could not signal main-window ready:", e);
    }
}

/** Hard ceiling: never leave the user stuck on the splash. */
export const SPLASH_FALLBACK_MS = 20_000;
