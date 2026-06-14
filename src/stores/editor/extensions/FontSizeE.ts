import { Mark } from "@tiptap/core";

export const FontSizeExtension = Mark.create({
    name: "fontSize",

    addAttributes() {
        return {
            size: {
                default: null,
                parseHTML: (element: HTMLElement) =>
                    element.style.fontSize || null,
                renderHTML: (attributes: { size?: string | null }) =>
                    attributes.size
                        ? { style: `font-size: ${attributes.size}` }
                        : {},
            },
        };
    },

    parseHTML() {
        return [{ tag: "span[style*=font-size]" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["span", HTMLAttributes, 0];
    },
});
