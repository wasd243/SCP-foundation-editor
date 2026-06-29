import { getEditor } from "../../editor.ts";
import {
    addFontSizeOverSelection,
    getActiveFootnoteFontSize,
} from "../../editor/extensions/WJtags/footnoteActiveView.ts";
import type { Level } from "@tiptap/extension-heading";

const defaultFontSize = 16;
const fontSizeStep = 2;
const minFontSize = 8;
const maxFontSize = 72;

function getCurrentFontSize() {
    const size =
        getActiveFootnoteFontSize() ?? getEditor()?.getAttributes("fontSize").size;

    if (typeof size !== "string") {
        return defaultFontSize;
    }

    const parsedSize = Number.parseInt(size, 10);
    return Number.isFinite(parsedSize) ? parsedSize : defaultFontSize;
}

function normalizeFontSize(size: number) {
    return Math.min(maxFontSize, Math.max(minFontSize, size));
}

export function setEditorFontSize(size: number) {
    if (
        addFontSizeOverSelection({ size: `${normalizeFontSize(size)}px` })
    ) {
        return;
    }

    const editor = getEditor();
    const markType = editor?.schema.marks.fontSize;

    if (!editor || !markType) {
        return;
    }

    const mark = markType.create({ size: `${normalizeFontSize(size)}px` });
    const { from, to } = editor.state.selection;
    let applied = false;

    editor
        .chain()
        .focus()
        .command(({ tr, dispatch }) => {
            tr.doc.nodesBetween(from, to, (node, pos) => {
                if (!node.isText) {
                    return;
                }

                tr.addMark(pos, pos + node.nodeSize, mark);
                applied = true;
            });

            if (!applied || !dispatch) {
                return applied;
            }

            dispatch(tr);
            return true;
        })
        .run();
}

export function increaseEditorFontSize() {
    setEditorFontSize(getCurrentFontSize() + fontSizeStep);
}

export function decreaseEditorFontSize() {
    setEditorFontSize(getCurrentFontSize() - fontSizeStep);
}

export function setEditorTitle(title: string) {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const { head } = editor.state.selection;

    const chain = editor.chain().focus().setTextSelection(head);

    if (title.toLowerCase() === "content") {
        chain.setParagraph().run();
        return;
    }

    const level = Math.min(6, Math.max(1, title.length - 1)) as Level;
    chain.setHeading({ level }).run();
}
