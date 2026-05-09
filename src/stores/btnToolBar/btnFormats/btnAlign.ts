import { getEditor, type EditorTextAlign } from "../../editor.ts";

export function setEditorAlign(align: EditorTextAlign) {
    getEditor()
        ?.chain()
        .focus()
        .updateAttributes("paragraph", { textAlign: align })
        .updateAttributes("heading", { textAlign: align })
        .run();
}

export function btnAlignIdleInterface() {}
