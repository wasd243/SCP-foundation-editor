import { reactive } from "vue";
import type { Editor } from "@tiptap/core";
import { type EditorTextAlign } from "../editor.ts";

/**
 * Word-style toolbar state: which formats the caret currently sits inside.
 * Buttons read these flags to light up; the values are recomputed from the
 * editor on every selection / transaction change.
 */
export interface ActiveFormatsState {
    bold: boolean;
    italic: boolean;
    underline: boolean;
    strike: boolean;
    subscript: boolean;
    superscript: boolean;
    blockquote: boolean;
    orderedList: boolean;
    bulletList: boolean;
    alignLeft: boolean;
    alignCenter: boolean;
    alignRight: boolean;
}

export const activeFormats = reactive<ActiveFormatsState>({
    bold: false,
    italic: false,
    underline: false,
    strike: false,
    subscript: false,
    superscript: false,
    blockquote: false,
    orderedList: false,
    bulletList: false,
    alignLeft: false,
    alignCenter: false,
    alignRight: false,
});

// Mirrors the node set the alignment command writes to (see btnAlign.ts).
const ALIGNABLE_NODES = new Set(["paragraph", "heading", "detailsSummary"]);

/**
 * Resolve the alignment of the block enclosing the caret. Returns `null` when
 * no alignment is set, which we treat as the default (left).
 */
function readBlockAlign(editor: Editor): EditorTextAlign | null {
    const { $from } = editor.state.selection;

    for (let depth = $from.depth; depth > 0; depth -= 1) {
        const node = $from.node(depth);

        if (ALIGNABLE_NODES.has(node.type.name)) {
            return (node.attrs.textAlign as EditorTextAlign | null) ?? null;
        }
    }

    return null;
}

function refreshActiveFormats(editor: Editor) {
    activeFormats.bold = editor.isActive("bold");
    activeFormats.italic = editor.isActive("italic");
    activeFormats.underline = editor.isActive("underline");
    activeFormats.strike = editor.isActive("strike");
    activeFormats.subscript = editor.isActive("subscript");
    activeFormats.superscript = editor.isActive("superscript");
    activeFormats.blockquote = editor.isActive("blockquote");
    activeFormats.orderedList = editor.isActive("orderedList");
    activeFormats.bulletList = editor.isActive("bulletList");

    const align = readBlockAlign(editor);
    // Left is the implicit default, so an unset alignment lights the left button.
    activeFormats.alignLeft = align === "left" || align === null;
    activeFormats.alignCenter = align === "center";
    activeFormats.alignRight = align === "right";
}

/**
 * Subscribe to the editor so toolbar highlight state tracks the caret. Call
 * once when the editor is created; the listeners live as long as the editor.
 */
export function attachActiveFormats(editor: Editor) {
    const update = () => refreshActiveFormats(editor);

    editor.on("selectionUpdate", update);
    editor.on("transaction", update);

    update();
}
