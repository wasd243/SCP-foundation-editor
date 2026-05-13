import { DOMSerializer } from "@tiptap/pm/model";
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

    const { state } = editor;
    const { $from, $to } = state.selection;
    const range = $from.blockRange($to);

    if (!range) {
        return;
    }

    const slice = state.doc.slice(range.start, range.end);
    const serializedContent = document.createElement("div");

    serializedContent.appendChild(DOMSerializer.fromSchema(state.schema).serializeFragment(slice.content));

    editor
        .chain()
        .focus()
        .insertContentAt(
            { from: range.start, to: range.end },
            `<details><summary><span class="wj-collapsible-show-text">+</span><span class="wj-collapsible-hide-text">-</span></summary><div data-type="detailsContent">${serializedContent.innerHTML || "<p></p>"}</div></details>`,
        )
        .setTextSelection(range.start + 2)
        .run();
}

export function btnBasicIdleInterface() {}
