import { save } from "@tauri-apps/plugin-dialog";
import { invoke } from "@tauri-apps/api/core";
import { dirname, basename } from "@tauri-apps/api/path";

export async function SaveFtml() {
    // open a save dialog
    const filePath = await save({
        filters: [{ name: "FTML", extensions: ["ftml", "txt"] }],
        defaultPath: "untitled.ftml",
    });

    if (!filePath) return; // user canceled the dialog

    const path = await dirname(filePath);
    const name = await basename(filePath);

    console.log("save active");

    await invoke("save_ftml", { path, name });
}
