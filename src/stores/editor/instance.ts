import type { Editor } from "@tiptap/vue-3";

let editor: Editor | null = null;

export function setEditor(instance: Editor | null) {
    editor = instance;
}

export function getEditor(): Editor | null {
    return editor;
}
