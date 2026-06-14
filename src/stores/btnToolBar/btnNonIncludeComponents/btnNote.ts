import type { JSONContent } from "@tiptap/core";

import { getEditor } from "../../editor.ts";
import noteTemplate from "../../json/note.json";

const template = noteTemplate as JSONContent;

function createNoteContent() {
    return JSON.parse(JSON.stringify(template)) as JSONContent;
}

export function insertEditorNote() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor.chain().focus().insertContent(createNoteContent()).run();
}
