import { Extension } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import type { Editor } from "@tiptap/vue-3";

export type EditorTextAlign = "left" | "center" | "right";

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
                        renderHTML: (attributes: { textAlign?: EditorTextAlign | null }) => {
                            if (!attributes.textAlign) {
                                return {};
                            }

                            return {
                                style: `text-align: ${attributes.textAlign}`,
                            };
                        },
                    },
                },
            },
        ];
    },
});

export const editorExtensions = [StarterKit, TextAlignExtension];

let editor: Editor | null = null;

export function setEditor(instance: Editor | null) {
    editor = instance;
}

export function getEditor(): Editor | null {
    return editor;
}
