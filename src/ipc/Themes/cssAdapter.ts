import { invoke } from "@tauri-apps/api/core";
import { parse, generate } from "css-tree";
import { getNecessaryCSS } from "./cssAdapter/getNecessaryCSS.ts";
import { renameCSS } from "./cssAdapter/renameCSS.ts";
import { addImportant } from "./cssAdapter/addImportant.ts";
import { inject } from "./cssAdapter/Inject.ts";

export async function connectCSSAdapter() {
    console.log("connecting css adapter");

    const rawCSS = await invoke<string>("get_theme");
    const ast = parse(rawCSS);
    getNecessaryCSS(ast);
    renameCSS(ast);
    addImportant(ast);
    inject(generate(ast));
}
