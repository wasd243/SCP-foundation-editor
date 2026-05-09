import { getEditor } from "../../editor.ts";

export function setEditorTextColor(color: string) {
    getEditor()?.chain().focus().setMark("textColor", { color }).run();
}

export function btnColorIdleInterface() {}
