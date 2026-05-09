import { getEditor } from "../../editor.ts";

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
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
        .run();
}

export function btnBasicIdleInterface() {}
