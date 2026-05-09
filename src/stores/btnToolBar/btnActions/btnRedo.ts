import { getEditor } from "../../editor.ts";

export function redoEditor() {
    getEditor()?.chain().focus().redo().run();
}
