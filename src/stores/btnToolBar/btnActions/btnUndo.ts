import { getEditor } from "../../editor.ts";

export function undoEditor() {
    getEditor()?.chain().focus().undo().run();
}
