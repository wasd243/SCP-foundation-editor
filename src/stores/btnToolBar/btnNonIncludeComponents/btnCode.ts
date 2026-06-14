import type { JSONContent } from "@tiptap/core";

import { getEditor } from "../../editor.ts";
import codeTemplate from "../../json/code.json";

const template = codeTemplate as JSONContent;

function createCodeBlockContent() {
    return JSON.parse(JSON.stringify(template)) as JSONContent;
}

export function insertEditorCode() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor.chain().focus().insertContent(createCodeBlockContent()).run();
}
