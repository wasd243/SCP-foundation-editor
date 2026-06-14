import { Mark } from "@tiptap/core";

export const TextColorExtension = Mark.create({
    name: "textColor",

    addAttributes() {
        return {
            color: {
                default: null,
                parseHTML: (element: HTMLElement) =>
                    element.style.color || null,
                renderHTML: (attributes: { color?: string | null }) =>
                    attributes.color
                        ? { style: `color: ${attributes.color}` }
                        : {},
            },
        };
    },

    parseHTML() {
        return [{ tag: "span[style*=color]" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["span", HTMLAttributes, 0];
    },
});
