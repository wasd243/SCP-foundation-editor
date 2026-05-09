import { Extension } from "@tiptap/core";
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

export const editorExtensions = [StarterKit, TextAlignExtension];
