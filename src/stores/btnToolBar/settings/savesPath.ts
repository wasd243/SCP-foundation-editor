import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

/**
 * Saves-path settings store.
 *
 * Shared reactive state + helpers for the "Saves folder" settings group.
 * The resolved saves directory is computed on the Rust side (`get_saves_path`);
 * the user's chosen path is persisted to the fixed settings file there. The
 * Vue component stays thin and only binds to / calls into these helpers.
 */

/** The currently resolved full saves path, for display. */
export const savesPath = ref<string>("");
/** Last error from picking a folder, or null when the last action succeeded. */
export const savesPathError = ref<string | null>(null);

/** Load the resolved saves path from the backend. */
export async function loadSavesPath(): Promise<void> {
    try {
        savesPath.value = await invoke<string>("get_saves_path");
        savesPathError.value = null;
    } catch (e) {
        savesPathError.value = String(e);
        console.error("[SavesPath] load failed:", e);
    }
}

/**
 * Prompt the user for a folder and set it as the custom saves path. The backend
 * validates writability before persisting; a bad path surfaces as an error and
 * leaves the current path unchanged.
 */
export async function pickSavesFolder(): Promise<void> {
    const chosen = await open({ directory: true, multiple: false });
    if (!chosen) return; // user canceled

    try {
        await invoke("set_saves_path", { path: chosen as string });
        await loadSavesPath();
    } catch (e) {
        savesPathError.value = String(e);
        console.error("[SavesPath] set failed:", e);
    }
}

/** Clear the custom path, reverting to the default `data_dir()/saves`. */
export async function resetSavesPath(): Promise<void> {
    try {
        await invoke("reset_saves_path");
        await loadSavesPath();
    } catch (e) {
        savesPathError.value = String(e);
        console.error("[SavesPath] reset failed:", e);
    }
}

/** Open the current saves directory in the OS file manager. */
export async function openSavesFolder(): Promise<void> {
    try {
        await invoke("open_saves_dir");
    } catch (e) {
        savesPathError.value = String(e);
        console.error("[SavesPath] open failed:", e);
    }
}
