import { invoke } from "@tauri-apps/api/core";

export async function SyncCSSToExporter(css: string | null | undefined) {
    if (!css || css.trim().length === 0) {
        return;
    }

    await invoke("export_css", {
        css,
    });
}
