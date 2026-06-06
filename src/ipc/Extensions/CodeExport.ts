import { SyncJSONToExporter } from "./CodeExport/getJSON.ts";
import { SyncCSSToExporter } from "./CodeExport/getCSS.ts";

export async function CodeExport() {
    await SyncJSONToExporter();
    // @ts-ignore
    await SyncCSSToExporter();
}
