import { getEditor } from "../../editor.ts";
import { setFootnoteMark } from "../../editor/extensions/WJtags/footnoteActiveView.ts";

export function setEditorTextColor(color: string) {
    if (setFootnoteMark("textColor", { color })) {
        return;
    }

    getEditor()?.chain().focus().setMark("textColor", { color }).run();
}

export function btnColorIdleInterface() {}
