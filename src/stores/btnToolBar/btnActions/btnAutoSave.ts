import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { SyncJSONToExporter } from "../../../ipc/Extensions/CodeExport/getJSON.ts";

/**
 * Auto-save store.
 *
 * Shared reactive state + the interval timer for the AutoSave toolbar button
 * and its settings panel. Components stay thin and only bind to / call into
 * the helpers exported here.
 *
 * Each tick regenerates the exporter output (`SyncJSONToExporter` →
 * `export_code` writes FINAL_OUTPUT_PATH) and then writes it to the fixed
 * `saves/autosave.ftml` file via the `auto_save_ftml` command (the
 * destination is hardcoded on the Rust side).
 */

/** Minimum interval to avoid hammering the exporter. */
export const AUTO_SAVE_MIN_SECONDS = 10;
/** Default interval: one minute. */
export const AUTO_SAVE_DEFAULT_SECONDS = 60;

export const autoSaveEnabled = ref(false);
export const autoSaveIntervalSeconds = ref(AUTO_SAVE_DEFAULT_SECONDS);
/** Epoch ms of the last successful save, or null if none yet. */
export const autoSaveLastSavedAt = ref<number | null>(null);
/** Increments on every successful save — drives the heartbeat animation. */
export const autoSavePulse = ref(0);
/** Last error message, or null when the last attempt succeeded. */
export const autoSaveError = ref<string | null>(null);

let timer: number | null = null;

async function runAutoSave(): Promise<void> {
    try {
        // Regenerate FINAL_OUTPUT_PATH from the current document, then write
        // it to the fixed saves/autosave.ftml destination.
        await SyncJSONToExporter();
        await invoke("auto_save_ftml");

        autoSaveLastSavedAt.value = Date.now();
        autoSaveError.value = null;
        autoSavePulse.value++;
    } catch (e) {
        autoSaveError.value = String(e);
        console.error("[AutoSave] save failed:", e);
    }
}

function clearTimer(): void {
    if (timer !== null) {
        clearInterval(timer);
        timer = null;
    }
}

function startTimer(): void {
    clearTimer();
    const seconds = Math.max(AUTO_SAVE_MIN_SECONDS, autoSaveIntervalSeconds.value);
    timer = window.setInterval(runAutoSave, seconds * 1000);
}

/** Toggle auto-save on/off. Starting begins the countdown; the first save
 *  happens after one full interval. */
export function toggleAutoSave(): void {
    autoSaveEnabled.value = !autoSaveEnabled.value;

    if (autoSaveEnabled.value) {
        autoSaveError.value = null;
        startTimer();
    } else {
        clearTimer();
    }
}

/** Update the interval (in seconds, clamped). Restarts the timer if running. */
export function setAutoSaveInterval(seconds: number): void {
    const next = Math.max(
        AUTO_SAVE_MIN_SECONDS,
        Math.floor(seconds) || AUTO_SAVE_DEFAULT_SECONDS,
    );
    autoSaveIntervalSeconds.value = next;

    if (autoSaveEnabled.value) {
        startTimer();
    }
}
