import { invoke } from "@tauri-apps/api/core";
import { getEditor } from "../../editor.ts";

/**
 * Dev helper: grab the editor's full ProseMirror JSON and write it to
 * `temp/dev_output.json` via the `log_and_write_json` Tauri command.
 */
export async function LogAndWriteJson() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const pmJSON = editor.getJSON();

    // debug output for testing
    console.log(pmJSON);

    await invoke("log_and_write_json", { json: pmJSON });
}
