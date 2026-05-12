import { mergeAttributes } from "@tiptap/core";
import { DetailsContent } from "@tiptap/extension-details";
import type { ViewMutationRecord } from "@tiptap/pm/view";

function limitToParentWidth(element: HTMLElement) {
    element.style.width = "100%";
    element.style.minWidth = "0";
    element.style.maxWidth = "100%";
    element.style.boxSizing = "border-box";
    element.style.overflowX = "auto";
    element.style.overflowWrap = "anywhere";
    element.style.wordBreak = "break-word";
}

export const DetailsContentExtension = DetailsContent.extend({
    addNodeView() {
        return ({ HTMLAttributes }) => {
            const dom = document.createElement("div");
            const attributes = mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
                "data-type": this.name,
                hidden: "hidden",
            });

            Object.entries(attributes).forEach(([key, value]) => dom.setAttribute(key, value));
            limitToParentWidth(dom);

            dom.addEventListener("toggleDetailsContent", () => {
                dom.toggleAttribute("hidden");
            });

            return {
                dom,
                contentDOM: dom,
                ignoreMutation(mutation: ViewMutationRecord) {
                    if (mutation.type === "selection") {
                        return false;
                    }

                    return !dom.contains(mutation.target) || dom === mutation.target;
                },
                update: updatedNode => updatedNode.type === this.type,
            };
        };
    },

    addKeyboardShortcuts() {
        return {};
    },
});
