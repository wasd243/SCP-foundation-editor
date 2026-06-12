import {basicSetup, EditorView} from 'codemirror';
import {css} from '@codemirror/lang-css';
import {invoke} from '@tauri-apps/api/core';
import { oneDark } from '@codemirror/theme-one-dark';
// import patch function here to update the editor CSS
import {patch_injectUserCss} from "../../../ipc/Extensions/CodeView/SyncToParser";

export async function initCSSEditor(parent: HTMLElement) {
    let initialContent = '';

    try {
        initialContent = await invoke<string>('patch_get_user_css');
    } catch {
        console.warn("No user CSS cache found."); // warn when no cache
    }

    return new EditorView({
        doc: initialContent,
        extensions: [basicSetup, css(), oneDark],
        parent,
    });
}

export async function SaveCSS(view: EditorView) {
    const content = view.state.doc.toString();
    await invoke('save_user_css_to_cache', { css: content });
    patch_injectUserCss(content);  // This patch function in `ipc\Extensions\CodeView\SynvToParser.ts`
}
