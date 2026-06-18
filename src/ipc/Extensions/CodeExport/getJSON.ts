import { invoke } from "@tauri-apps/api/core";
import { getEditor } from "../../../stores/editor.ts";

export async function SyncJSONToExporter() {
    const editor = getEditor();

    if (!editor) {
        return null;
    }

    const pmJSON = editor.getJSON();

    // debug output for testing
    // console.log(pmJSON);

    return await invoke<string>("export_code", {
        json: JSON.stringify(pmJSON),
    });
}
