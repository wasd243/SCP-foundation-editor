import { mergeAttributes, Node } from "@tiptap/core";
import type { Editor } from "@tiptap/core";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import type { ResolvedPos } from "@tiptap/pm/model";
import { Plugin } from "@tiptap/pm/state";
import type { EditorState, Transaction } from "@tiptap/pm/state";

const TAB_VIEW_BUTTON_MAX_LABEL_LENGTH = 80;

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
                    name === "hidden"
                        ? element.hasAttribute("hidden")
                            ? ""
                            : null
                        : element.getAttribute(name),
                renderHTML: (attributes: Record<string, string | null>) =>
                    attributes[name] === null
                        ? {}
                        : { [name]: attributes[name] },
            },
        ]),
    );
}

function syncPreservedAttributes(
    element: HTMLElement,
    attributes: Record<string, string | null>,
) {
    preservedAttributes.forEach((name) => {
        element.removeAttribute(name);

        const value = attributes[name];

        if (value !== null && value !== undefined) {
            element.setAttribute(name, value);
        }
    });
}

function limitToParentWidth(element: HTMLElement) {
    element.style.width = "100%";
    element.style.minWidth = "0";
    element.style.maxWidth = "100%";
    element.style.boxSizing = "border-box";
}

function createBoundedNodeView(tagName: string) {
    return ({
        node,
        HTMLAttributes,
    }: {
        node: ProseMirrorNode;
        HTMLAttributes: Record<string, string | null>;
    }) => {
        const dom = document.createElement(tagName);
        const syncNode = (currentNode: ProseMirrorNode) => {
            syncPreservedAttributes(
                dom,
                mergeAttributes(HTMLAttributes, currentNode.attrs),
            );
            limitToParentWidth(dom);
        };

        syncNode(node);

        return {
            dom,
            contentDOM: dom,
            update: (updatedNode: ProseMirrorNode) => {
                if (updatedNode.type !== node.type) return false;

                syncNode(updatedNode);

                return true;
            },
        };
    };
}

function countChars(text: string) {
    return Array.from(text).length;
}

function findTabViewButton($pos: ResolvedPos) {
    for (let depth = $pos.depth; depth > 0; depth -= 1) {
        const node = $pos.node(depth);

        if (node.type.name === "tabViewButton") {
            return {
                node,
                pos: $pos.before(depth),
            };
        }
    }

    return null;
}

function getSelectedTabViewButtonTextLength(
    state: EditorState,
    button: { node: ProseMirrorNode; pos: number },
) {
    const { from, to } = state.selection;
    const buttonStart = button.pos + 1;
    const buttonEnd = button.pos + button.node.nodeSize - 1;
    const selectedFrom = Math.max(from, buttonStart);
    const selectedTo = Math.min(to, buttonEnd);

    if (selectedTo <= selectedFrom) {
        return 0;
    }

    return countChars(state.doc.textBetween(selectedFrom, selectedTo));
}

function shouldBlockTabViewButtonInput(state: EditorState, inputText: string) {
    const { $from, $to } = state.selection;
    const fromButton = findTabViewButton($from);
    const toButton = findTabViewButton($to);

    if (!fromButton && !toButton) {
        return false;
    }

    if (!fromButton || !toButton || fromButton.pos !== toButton.pos) {
        return true;
    }

    const selectedLength = getSelectedTabViewButtonTextLength(
        state,
        fromButton,
    );
    const nextLength =
        countChars(fromButton.node.textContent) -
        selectedLength +
        countChars(inputText);

    return nextLength > TAB_VIEW_BUTTON_MAX_LABEL_LENGTH;
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

        tr.setNodeMarkup(
            buttonListPos + 1 + offset,
            undefined,
            {
                ...button.attrs,
                "aria-selected":
                    button.attrs.id === buttonId ? "true" : "false",
                tabindex: button.attrs.id === buttonId ? "0" : "-1",
            },
            button.marks,
        );
    });

    if (!hasButton) return false;

    panelList.forEach((panel, offset) => {
        tr.setNodeMarkup(
            panelListPos + 1 + offset,
            undefined,
            {
                ...panel.attrs,
                hidden: panel.attrs.id === panelId ? null : "",
            },
            panel.marks,
        );
    });

    return true;
}

function NoEnterInTabViewButton(editor: Editor) {
    const { $from, $to } = editor.state.selection;
    const positions = [$from, $to];

    return positions.some(($pos) => {
        for (let depth = $pos.depth; depth > 0; depth -= 1) {
            if ($pos.node(depth).type.name === "tabViewButton") {
                return true;
            }
        }

        return false;
    });
}

function selectionInsideTabViewPanel(editor: Editor) {
    const { $from, $to } = editor.state.selection;
    const positions = [$from, $to];

    return positions.some(($pos) => {
        for (let depth = $pos.depth; depth > 0; depth -= 1) {
            if ($pos.node(depth).type.name === "tabViewPanel") {
                return true;
            }
        }

        return false;
    });
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

    addNodeView() {
        return createBoundedNodeView("wj-tabs");
    },

    addKeyboardShortcuts() {
        return {
            Enter: () => NoEnterInTabViewButton(this.editor),
        };
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

                        if (button.getAttribute("aria-selected") === "true") {
                            return false;
                        }

                        const buttonId = button.getAttribute("id");
                        const panelId = button.getAttribute("aria-controls");
                        if (!buttonId || !panelId) return false;

                        const tr = view.state.tr;
                        let changed = false;

                        view.state.doc.descendants((node, pos) => {
                            if (node.type.name !== "tabView") return true;

                            if (
                                switchTabViewTab(
                                    node,
                                    pos,
                                    buttonId,
                                    panelId,
                                    tr,
                                )
                            ) {
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
                    handleTextInput: (view, _from, _to, text) =>
                        shouldBlockTabViewButtonInput(view.state, text),
                    handlePaste: (view, event) => {
                        const text =
                            event.clipboardData?.getData("text/plain") ?? "";

                        return (
                            text.length > 0 &&
                            shouldBlockTabViewButtonInput(view.state, text)
                        );
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

    addNodeView() {
        return createBoundedNodeView("div");
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

    addNodeView() {
        return ({ node, HTMLAttributes }) => {
            const dom = document.createElement("wj-tabs-button");
            const label = document.createElement("span");

            label.className = "wj-tabs-button-label";
            dom.append(label);

            const syncButton = (currentNode: ProseMirrorNode) => {
                syncPreservedAttributes(
                    dom,
                    mergeAttributes(HTMLAttributes, currentNode.attrs),
                );
                dom.title =
                    currentNode.textContent ||
                    currentNode.attrs["aria-label"] ||
                    "";
            };

            syncButton(node);

            return {
                dom,
                contentDOM: label,
                update: (updatedNode) => {
                    if (updatedNode.type !== this.type) return false;

                    syncButton(updatedNode);

                    return true;
                },
            };
        };
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

    addNodeView() {
        return createBoundedNodeView("div");
    },
});

export const TabViewPanelExtension = Node.create({
    name: "tabViewPanel",
    content: "block+",
    defining: true,
    isolating: true,

    addAttributes: addPreservedAttributes,

    parseHTML() {
        return [{ tag: "div.wj-tabs-panel" }];
    },

    renderHTML({ HTMLAttributes }) {
        return ["div", mergeAttributes(HTMLAttributes), 0];
    },

    addNodeView() {
        return createBoundedNodeView("div");
    },

    addKeyboardShortcuts() {
        return {
            Enter: () => {
                if (!selectionInsideTabViewPanel(this.editor)) return false;

                return this.editor.commands.splitBlock();
            },
        };
    },
});

export const TabViewExtensions = [
    TabViewExtension,
    TabViewButtonListExtension,
    TabViewButtonExtension,
    TabViewPanelListExtension,
    TabViewPanelExtension,
];
