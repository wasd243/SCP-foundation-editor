import { Extension, Mark } from "@tiptap/core";
import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";
import type { EditorTextAlign } from "./types";

const TextAlignExtension = Extension.create({
    name: "textAlign",
    addGlobalAttributes() {
        return [
            {
                types: ["heading", "paragraph"],
                attributes: {
                    textAlign: {
                        default: null,
                        parseHTML: (element: HTMLElement) => element.style.textAlign || null,
                        renderHTML: (attributes: { textAlign?: EditorTextAlign | null }) =>
                            attributes.textAlign ? { style: `text-align: ${attributes.textAlign}` } : {},
                    },
                },
            },
        ];
    },
});

const SubscriptExtension = Mark.create({
    name: "subscript",

    parseHTML() {
        return [{ tag: "sub" }];
    },

    renderHTML() {
        return ["sub", 0];
    },
});

const SuperscriptExtension = Mark.create({
    name: "superscript",

    parseHTML() {
        return [{ tag: "sup" }];
    },

    renderHTML() {
        return ["sup", 0];
    },
});

export const editorExtensions = [StarterKit, Underline, TextAlignExtension, SubscriptExtension, SuperscriptExtension];
