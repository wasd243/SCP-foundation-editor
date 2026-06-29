import { getEditor } from "../../editor.ts";
import { toggleFootnoteMark } from "../../editor/extensions/WJtags/footnoteActiveView.ts";

export function toggleEditorBold() {
    if (toggleFootnoteMark("bold")) {
        return;
    }

    getEditor()?.chain().focus().toggleMark("bold").run();
}

export function toggleEditorItalic() {
    if (toggleFootnoteMark("italic")) {
        return;
    }

    getEditor()?.chain().focus().toggleMark("italic").run();
}

export function toggleEditorUnderline() {
    if (toggleFootnoteMark("underline")) {
        return;
    }

    getEditor()?.chain().focus().toggleMark("underline").run();
}

export function toggleEditorStrikethrough() {
    if (toggleFootnoteMark("strike")) {
        return;
    }

    getEditor()?.chain().focus().toggleMark("strike").run();
}

export function toggleEditorSubscript() {
    if (toggleFootnoteMark("subscript", "superscript")) {
        return;
    }

    getEditor()
        ?.chain()
        .focus()
        .unsetMark("superscript")
        .toggleMark("subscript")
        .run();
}

export function toggleEditorSuperscript() {
    if (toggleFootnoteMark("superscript", "subscript")) {
        return;
    }

    getEditor()
        ?.chain()
        .focus()
        .unsetMark("subscript")
        .toggleMark("superscript")
        .run();
}

export function toggleEditorQuote() {
    getEditor()?.chain().focus().toggleWrap("blockquote").run();
}

export function insertEditorTable() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    // Seed every cell with placeholder text. Empty cells render as blank
    // Wikidot cells (`|| ||`) on export and are awkward to click into, so the
    // inserted table ships with visible "TABLE" content the user overwrites.
    const cell = (type: "tableHeader" | "tableCell") => ({
        type,
        content: [
            {
                type: "paragraph",
                content: [{ type: "text", text: "TABLE" }],
            },
        ],
    });

    const row = (type: "tableHeader" | "tableCell") => ({
        type: "tableRow",
        content: [cell(type), cell(type)],
    });

    editor
        .chain()
        .focus()
        .insertContent({
            type: "table",
            content: [row("tableHeader"), row("tableCell")],
        })
        .run();
}

export function insertEditorHorizontalRule() {
    getEditor()?.chain().focus().setHorizontalRule().run();
}

export function insertEditorCollapsible() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor.chain().focus().setDetails().run();
}

export function btnBasicIdleInterface() {}
