import { findParentNode, Mark, mergeAttributes } from "@tiptap/core";
import { Details, DetailsSummary } from "@tiptap/extension-details";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import type { ViewMutationRecord } from "@tiptap/pm/view";

function syncAlign(element: HTMLElement, align: string | null) {
    element.classList.remove("align-left", "align-center", "align-right", "align-justify");

    if (!align) {
        element.style.removeProperty("text-align");
        return;
    }

    element.classList.add(`align-${align}`);
    element.style.textAlign = align;
}

export const CollapsibleShowTextMark = Mark.create({
    name: "collapsibleShowText",

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
    addKeyboardShortcuts() {
        const deleteEmptyDetails = (key: "Backspace" | "Delete") => {
            const { state, view } = this.editor;
            const { selection } = state;
            const detailsSummary = findParentNode(node => node.type === this.type)(selection);

            if (!detailsSummary) {
                return false;
            }

            if (detailsSummary.node.textContent.length > 0) {
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
