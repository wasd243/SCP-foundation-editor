import {getEditor} from "../../editor.ts";

export function toggleEditorBold() {
    getEditor()?.chain().focus().toggleMark("bold").run();
}

export function toggleEditorItalic() {
    getEditor()?.chain().focus().toggleMark("italic").run();
}

export function toggleEditorUnderline() {
    getEditor()?.chain().focus().toggleMark("underline").run();
}

export function toggleEditorStrikethrough() {
    getEditor()?.chain().focus().toggleMark("strike").run();
}

export function toggleEditorSubscript() {
    getEditor()?.chain().focus().unsetMark("superscript").toggleMark("subscript").run();
}

export function toggleEditorSuperscript() {
    getEditor()?.chain().focus().unsetMark("subscript").toggleMark("superscript").run();
}

export function toggleEditorQuote() {
    getEditor()?.chain().focus().toggleWrap("blockquote").run();
}

export function insertEditorTable() {
    getEditor()
        ?.chain()
        .focus()
        .insertTable({rows: 2, cols: 2, withHeaderRow: true})
        .run();
}

export function insertEditorHorizontalRule() {
    getEditor()
        ?.chain()
        .focus()
        .setHorizontalRule()
        .run();
}

export function insertEditorCollapsible() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor
        .chain()
        .focus()
        .setDetails()
        .run();
}

export function btnBasicIdleInterface() {
}
