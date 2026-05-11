import { mergeAttributes } from "@tiptap/core";
import { Details } from "@tiptap/extension-details";
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
