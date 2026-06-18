import { invoke } from "@tauri-apps/api/core";
import postcss from "postcss";
import getNecessaryCSS from "./cssAdapter/getNecessaryCSS.ts";
import renameCSS from "./cssAdapter/renameCSS.ts";
import addImportant from "./cssAdapter/addImportant.ts";
import { inject } from "./cssAdapter/Inject.ts";

export async function connectCSSAdapter() {
    const rawCSS = await invoke<string>("get_theme");
    const result = await postcss([
        getNecessaryCSS(),
        renameCSS(),
        addImportant(),
    ]).process(rawCSS, { from: undefined });
    inject(result.css);
}
