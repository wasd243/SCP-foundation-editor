import { getEditor } from "../../editor.ts";

export function insertEditorFootnote() {
    getEditor()?.chain().focus().insertFootnote().run();
}
