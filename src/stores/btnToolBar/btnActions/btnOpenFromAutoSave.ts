import { invoke } from "@tauri-apps/api/core";

/**
 * Open the latest auto-saved document (`saves/autosave.ftml`) directly into
 * the editor, skipping the file dialog.
 *
 * The hardcoded path lives on the Rust side (`read_autosave_ftml`). Like
 * {@link OpenFtml}, this posts the raw Wikitext so `SyncToParser.ts` handles
 * the parsing — no `invoke("parse_wikidot")` here.
 */
export async function OpenFromAutoSave() {
    let content: string;
    try {
        content = await invoke<string>("read_autosave_ftml");
    } catch (e) {
        console.error("[AutoSave] open failed:", e);
        return;
    }

    window.postMessage(
        { type: "code-view-content-changed", payload: content },
        "*",
    );
}
