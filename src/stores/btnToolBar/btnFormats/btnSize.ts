import { getEditor } from "../../editor.ts";
import type { Level } from "@tiptap/extension-heading";

const defaultFontSize = 16;
const fontSizeStep = 2;
const minFontSize = 8;
const maxFontSize = 72;

function getCurrentFontSize() {
    const size = getEditor()?.getAttributes("fontSize").size;

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
    getEditor()
        ?.chain()
        .focus()
        .setMark("fontSize", { size: `${normalizeFontSize(size)}px` })
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

    if (title === "Content") {
        editor.chain().focus().setParagraph().run();
        return;
    }

    // Convert title numbers to heading level
    const level = Math.min(6, Math.max(1, title.length - 1)) as Level;
    editor.chain().focus().toggleHeading({ level }).run();
}

export function btnSizeIdleInterface() {}
