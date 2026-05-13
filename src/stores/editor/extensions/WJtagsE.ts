// WJtagsE.ts is make for allowing wikijump custom tags render in the editor
import { Node } from "@tiptap/core";

function getElementAttributes(element: HTMLElement) {
    return Object.fromEntries(
        Array.from(element.attributes).map(attribute => [attribute.name, attribute.value]),
    );
}

function hasWJClass(element: HTMLElement) {
    return Array.from(element.classList).some(className => className.startsWith("wj"));
}

function shouldPreserveElement(element: HTMLElement) {
    const tagName = element.tagName.toLowerCase();

    return tagName.startsWith("wj") || (tagName === "div" && hasWJClass(element));
}

export const WJTagExtension = Node.create({
    name: "wjTag",
    priority: 1,
    group: "block",
    content: "block*",
    defining: true,

    addAttributes() {
        return {
            tagName: {
                default: "div",
            },
            htmlAttributes: {
                default: {},
            },
        };
    },

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !shouldPreserveElement(element)) {
                        return false;
                    }

                    return {
                        tagName: element.tagName.toLowerCase(),
                        htmlAttributes: getElementAttributes(element),
                    };
                },
            },
        ];
    },

    renderHTML({ node }) {
        return [node.attrs.tagName, node.attrs.htmlAttributes, 0];
    },
});
