import { getEditor } from "../../editor.ts";

export function toggleEditorOrderedList() {
    getEditor()?.chain().focus().toggleOrderedList().run();
}

export function toggleEditorUnorderedList() {
    getEditor()?.chain().focus().toggleBulletList().run();
}

export function btnListIdleInterface() {}
