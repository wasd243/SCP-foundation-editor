import { Extension } from "@tiptap/core";
import type { EditorTextAlign } from "../types.ts";

export const TextAlignExtension = Extension.create({
    name: "textAlign",
    addGlobalAttributes() {
        return [
            {
                types: ["heading", "paragraph", "detailsSummary"],
                attributes: {
                    textAlign: {
                        default: null,
                        parseHTML: (element: HTMLElement) =>
                            element.style.textAlign || null,
                        renderHTML: (attributes: {
                            textAlign?: EditorTextAlign | null;
                        }) =>
                            attributes.textAlign
                                ? {
                                      style: `text-align: ${attributes.textAlign}`,
                                  }
                                : {},
                    },
                },
            },
        ];
    },
});
