import { mergeAttributes, Node } from "@tiptap/core";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { Plugin } from "@tiptap/pm/state";
import type { Transaction } from "@tiptap/pm/state";

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

function switchTabViewTab(
    tabView: ProseMirrorNode,
    tabViewPos: number,
    buttonId: string,
    panelId: string,
    tr: Transaction,
) {
    const buttonList = tabView.child(0);
    const panelList = tabView.child(1);
    const buttonListPos = tabViewPos + 1;
    const panelListPos = buttonListPos + buttonList.nodeSize;
    let hasButton = false;

    buttonList.forEach((button, offset) => {
        if (button.attrs.id === buttonId) {
            hasButton = true;
        }

        tr.setNodeMarkup(buttonListPos + 1 + offset, undefined, {
            ...button.attrs,
            "aria-selected": button.attrs.id === buttonId ? "true" : "false",
            tabindex: button.attrs.id === buttonId ? "0" : "-1",
        }, button.marks);
    });

    if (!hasButton) return false;

    panelList.forEach((panel, offset) => {
        tr.setNodeMarkup(panelListPos + 1 + offset, undefined, {
            ...panel.attrs,
            hidden: panel.attrs.id === panelId ? null : "",
        }, panel.marks);
    });

    return true;
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

    addProseMirrorPlugins() {
        return [
            new Plugin({
                props: {
                    handleClick: (view, _pos, event) => {
                        if (event.button !== 0) return false;

                        const target = event.target as HTMLElement | null;
                        const button = target?.closest("wj-tabs-button");
                        if (!button) return false;

                        const buttonId = button.getAttribute("id");
                        const panelId = button.getAttribute("aria-controls");
                        if (!buttonId || !panelId) return false;

                        const tr = view.state.tr;
                        let changed = false;

                        view.state.doc.descendants((node, pos) => {
                            if (node.type.name !== "tabView") return true;

                            if (switchTabViewTab(node, pos, buttonId, panelId, tr)) {
                                changed = true;
                                return false;
                            }

                            return true;
                        });

                        if (!changed) return false;

                        event.preventDefault();
                        view.dispatch(tr);

                        return true;
                    },
                },
            }),
        ];
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
