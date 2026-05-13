// DetailE.ts is a collapsible block extension for Tiptap
import { findParentNode, Mark, mergeAttributes } from "@tiptap/core";
import { Details, DetailsSummary } from "@tiptap/extension-details";
import { Fragment, type Node as ProseMirrorNode } from "@tiptap/pm/model";
import { Plugin } from "@tiptap/pm/state";
import type { ViewMutationRecord } from "@tiptap/pm/view";

const EMPTY_COLLAPSIBLE_TEXT = "\u200B";

function syncAlign(element: HTMLElement, align: string | null) {
    element.classList.remove("align-left", "align-center", "align-right", "align-justify");

    if (!align) {
        element.style.removeProperty("text-align");
        return;
    }

    element.classList.add(`align-${align}`);
    element.style.textAlign = align;
}

function stripEmptyCollapsibleText(text: string) {
    return text.replaceAll(EMPTY_COLLAPSIBLE_TEXT, "");
}

function getSummaryText(summary: ProseMirrorNode) {
    return stripEmptyCollapsibleText(summary.textContent);
}

export const CollapsibleShowTextMark = Mark.create({
    name: "collapsibleShowText",
    inclusive: false,
    excludes: "collapsibleHideText",

    parseHTML() {
        return [
            {
                tag: "span.wj-collapsible-show-text",
            },
        ];
    },

    renderHTML({ HTMLAttributes }) {
        return ["span", mergeAttributes(HTMLAttributes, { class: "wj-collapsible-show-text" }), 0];
    },
});

export const CollapsibleHideTextMark = Mark.create({
    name: "collapsibleHideText",
    inclusive: false,
    excludes: "collapsibleShowText",

    parseHTML() {
        return [
            {
                tag: "span.wj-collapsible-hide-text",
            },
        ];
    },

    renderHTML({ HTMLAttributes }) {
        return ["span", mergeAttributes(HTMLAttributes, { class: "wj-collapsible-hide-text" }), 0];
    },
});

// Details Extension for collapsible blocks
export const DetailsExtension = Details.extend({
    selectable: false,

    addNodeView() {
        return ({ editor, node, HTMLAttributes }) => {
            const dom = document.createElement("div");
            const toggle = document.createElement("button");
            const content = document.createElement("div");

            const syncNodeAttributes = (currentNode: ProseMirrorNode) => {
                const attributes = mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
                    "data-type": this.name,
                });

                Object.entries(attributes).forEach(([key, value]) => dom.setAttribute(key, value));

                const align = currentNode.attrs.textAlign ?? null;
                syncAlign(dom, align);
                syncAlign(toggle, align);
                syncAlign(content, align);
            };

            syncNodeAttributes(node);

            toggle.type = "button";
            toggle.tabIndex = -1;
            toggle.contentEditable = "false";
            toggle.setAttribute("contenteditable", "false");
            toggle.setAttribute("draggable", "false");
            dom.append(toggle);
            dom.append(content);

            const renderToggleButton = (currentNode: ProseMirrorNode) => {
                this.options.renderToggleButton({
                    element: toggle,
                    isOpen: dom.classList.contains(this.options.openClassName),
                    node: currentNode,
                });
            };

            const toggleDetailsContent = (currentNode: ProseMirrorNode) => {
                dom.classList.toggle(this.options.openClassName);
                renderToggleButton(currentNode);

                const detailsContent = content.querySelector(':scope > div[data-type="detailsContent"]');
                detailsContent?.dispatchEvent(new Event("toggleDetailsContent"));
            };

            renderToggleButton(node);

            toggle.addEventListener("mousedown", event => {
                event.preventDefault();
            });

            toggle.addEventListener("click", () => {
                toggleDetailsContent(node);
                editor.commands.focus(undefined, { scrollIntoView: false });
            });

            return {
                dom,
                contentDOM: content,
                ignoreMutation(mutation: ViewMutationRecord) {
                    if (mutation.type === "selection") {
                        return false;
                    }

                    return toggle.contains(mutation.target) || !dom.contains(mutation.target) || dom === mutation.target;
                },
                stopEvent(event: Event) {
                    return toggle.contains(event.target as Node);
                },
                update: (updatedNode: ProseMirrorNode) => {
                    if (updatedNode.type !== this.type) {
                        return false;
                    }

                    syncNodeAttributes(updatedNode);
                    renderToggleButton(updatedNode);

                    return true;
                },
            };
        };
    },
});

export const DetailsSummaryExtension = DetailsSummary.extend({
    addProseMirrorPlugins() {
        return [
            new Plugin({
                appendTransaction: (_transactions, _oldState, newState) => {
                    const { schema } = newState;
                    const showTextMark = schema.marks.collapsibleShowText;
                    const hideTextMark = schema.marks.collapsibleHideText;

                    if (!showTextMark || !hideTextMark) {
                        return null;
                    }

                    const transaction = newState.tr;
                    let changed = false;

                    newState.doc.descendants((node, pos) => {
                        if (node.type !== this.type) {
                            return true;
                        }

                        let showText = "";
                        let hideText = "";
                        let showRawText = "";
                        let hideRawText = "";
                        let hasShowText = false;
                        let hasHideText = false;
                        let hasInvalidText = false;
                        let currentTextType: "show" | "hide" | null = null;

                        node.descendants(child => {
                            if (!child.isText) {
                                return true;
                            }

                            const text = child.text ?? "";
                            const hasShowMark = child.marks.some(mark => mark.type === showTextMark);
                            const hasHideMark = child.marks.some(mark => mark.type === hideTextMark);

                            if (hasShowMark && !hasHideMark) {
                                hasShowText = true;
                                currentTextType = "show";
                                showRawText += text;
                                showText += stripEmptyCollapsibleText(text);
                                return true;
                            }

                            if (hasHideMark && !hasShowMark) {
                                hasHideText = true;
                                currentTextType = "hide";
                                hideRawText += text;
                                hideText += stripEmptyCollapsibleText(text);
                                return true;
                            }

                            const cleanText = stripEmptyCollapsibleText(text);

                            if (cleanText.length > 0) {
                                hasInvalidText = true;

                                if (currentTextType === "hide") {
                                    hideText += cleanText;
                                } else {
                                    showText += cleanText;
                                }
                            }

                            return true;
                        });

                        const nextShowText = showText || EMPTY_COLLAPSIBLE_TEXT;
                        const nextHideText = hideText || EMPTY_COLLAPSIBLE_TEXT;
                        const needsNormalize = hasInvalidText
                            || !hasShowText
                            || !hasHideText
                            || showRawText !== nextShowText
                            || hideRawText !== nextHideText;

                        if (!needsNormalize) {
                            return false;
                        }

                        transaction.replaceWith(
                            transaction.mapping.map(pos + 1),
                            transaction.mapping.map(pos + node.nodeSize - 1),
                            Fragment.fromArray([
                                schema.text(nextShowText, [showTextMark.create()]),
                                schema.text(nextHideText, [hideTextMark.create()]),
                            ]),
                        );
                        changed = true;

                        return false;
                    });

                    return changed ? transaction : null;
                },
            }),
        ];
    },

    addKeyboardShortcuts() {
        const deleteEmptyDetails = (key: "Backspace" | "Delete") => {
            const { state, view } = this.editor;
            const { selection } = state;
            const detailsSummary = findParentNode(node => node.type === this.type)(selection);

            if (!detailsSummary) {
                return false;
            }

            if (getSummaryText(detailsSummary.node).length > 0) {
                const { $from, empty } = selection;
                const summaryStart = detailsSummary.pos + 1;
                const summaryEnd = detailsSummary.pos + detailsSummary.node.nodeSize - 1;

                return empty && (key === "Backspace" ? $from.pos === summaryStart : $from.pos === summaryEnd);
            }

            const details = findParentNode(node => node.type.name === "details")(selection);

            if (!details) {
                return true;
            }

            const paragraph = state.schema.nodes.paragraph?.createAndFill();
            const transaction = state.doc.childCount === 1 && paragraph
                ? state.tr.replaceWith(details.pos, details.pos + details.node.nodeSize, paragraph)
                : state.tr.delete(details.pos, details.pos + details.node.nodeSize);

            transaction.scrollIntoView();
            view.dispatch(transaction);

            return true;
        };

        return {
            Enter: () => {
                const detailsSummary = findParentNode(node => node.type === this.type)(this.editor.state.selection);

                return Boolean(detailsSummary);
            },
            Backspace: () => deleteEmptyDetails("Backspace"),
            Delete: () => deleteEmptyDetails("Delete"),
        };
    },
});

export const CollapsibleTextExtensions = [
    CollapsibleShowTextMark,
    CollapsibleHideTextMark,
];
