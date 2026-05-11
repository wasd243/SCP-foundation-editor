import { mergeAttributes, Node } from "@tiptap/core";

const preservedAttributes = [
    "class",
    "id",
    "role",
    "aria-label",
    "aria-selected",
    "aria-controls",
    "aria-labelledby",
    "tabindex",
    "hidden",
];

function addPreservedAttributes() {
    return Object.fromEntries(
        preservedAttributes.map((name) => [
            name,
            {
                default: null,
                parseHTML: (element: HTMLElement) =>
                    name === "hidden" ? (element.hasAttribute("hidden") ? "" : null) : element.getAttribute(name),
                renderHTML: (attributes: Record<string, string | null>) =>
                    attributes[name] === null ? {} : { [name]: attributes[name] },
            },
        ]),
    );
}

export const TabViewExtension = Node.create({
    name: "tabView",
    group: "block",
    content: "tabViewButtonList tabViewPanelList",

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "wj-tabs" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["wj-tabs", mergeAttributes(HTMLAttributes), 0];
    },
});

export const TabViewButtonListExtension = Node.create({
    name: "tabViewButtonList",
    content: "tabViewButton+",

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "div.wj-tabs-button-list" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["div", mergeAttributes(HTMLAttributes), 0];
    },
});

export const TabViewButtonExtension = Node.create({
    name: "tabViewButton",
    content: "text*",
    defining: true,

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "wj-tabs-button" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["wj-tabs-button", mergeAttributes(HTMLAttributes), 0];
    },
});

export const TabViewPanelListExtension = Node.create({
    name: "tabViewPanelList",
    content: "tabViewPanel+",

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "div.wj-tabs-panel-list" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["div", mergeAttributes(HTMLAttributes), 0];
    },
});

export const TabViewPanelExtension = Node.create({
    name: "tabViewPanel",
    content: "block+",
    defining: true,

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "div.wj-tabs-panel" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["div", mergeAttributes(HTMLAttributes), 0];
    },
});

export const TabViewExtensions = [
    TabViewExtension,
    TabViewButtonListExtension,
    TabViewButtonExtension,
    TabViewPanelListExtension,
    TabViewPanelExtension,
];
