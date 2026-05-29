import {invoke} from "@tauri-apps/api/core";
import {getEditor} from "../../../stores/editor.ts";

export async function SyncJSONToExporter() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const pmJSON = editor.getJSON();

    // debug output for testing
    console.log(pmJSON);

    await invoke("export_json", {
        json: JSON.stringify(pmJSON),
    });
}
