// Inline footnote node, implemented directly from the ProseMirror official
// footnote example (https://prosemirror.net/examples/footnote/).
//
// NOTE: we do NOT use `@aeaton/prosemirror-footnotes`' `footnoteView` — its
// compiled v2.0.2 node view returns an object without a `dom` property, so
// ProseMirror cannot mount it and silently falls back to plain `renderHTML`
// (no tooltip, content rendered inline). The official class-based view below
// owns `this.dom`, so it mounts correctly.
//
// The node is an `atom` carrying `text*` content edited through a nested
// sub-editor that opens when the footnote is selected (clicked). Numbering is a
// pure CSS counter on the `<footnote>` element (see default.scss), never stored
// in attrs.
//
// The Rust parser emits `<footnote>…</footnote>`, and the `ltmf` exporter turns
// a node of type "footnote" back into `[[footnote]]…[[/footnote]]`.
import { Node, mergeAttributes } from "@tiptap/core";
import type { NodeViewRenderer, NodeViewRendererProps } from "@tiptap/core";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { EditorState, NodeSelection } from "@tiptap/pm/state";
import type { Transaction } from "@tiptap/pm/state";
import { StepMap } from "@tiptap/pm/transform";
import { EditorView } from "@tiptap/pm/view";
import { keymap } from "@tiptap/pm/keymap";
import { undo, redo } from "@tiptap/pm/history";
import {
    setActiveFootnoteView,
    clearActiveFootnoteView,
} from "./footnoteActiveView.ts";

declare module "@tiptap/core" {
    interface Commands<ReturnType> {
        footnote: {
            // Insert an empty footnote at the current selection.
            insertFootnote: () => ReturnType;
        };
    }
}

// Class node view mirroring the PM official footnote example. Editing happens in
// a nested EditorView whose document is the footnote node; inner steps are
// mapped back onto the outer document.
class FootnoteView {
    dom: HTMLElement;
    node: ProseMirrorNode;
    outerView: EditorView;
    getPos: () => number | undefined;
    innerView: EditorView | null;

    constructor(
        node: ProseMirrorNode,
        view: EditorView,
        getPos: () => number | undefined,
    ) {
        this.node = node;
        this.outerView = view;
        this.getPos = getPos;
        this.innerView = null;
        this.dom = document.createElement("footnote");
    }

    selectNode() {
        this.dom.classList.add("ProseMirror-selectednode");
        if (!this.innerView) {
            this.open();
        }
    }

    deselectNode() {
        this.dom.classList.remove("ProseMirror-selectednode");
        if (this.innerView) {
            this.close();
        }
    }

    open() {
        const tooltip = this.dom.appendChild(document.createElement("div"));
        tooltip.className = "footnote-tooltip";

        this.innerView = new EditorView(tooltip, {
            state: EditorState.create({
                doc: this.node,
                plugins: [
                    keymap({
                        "Mod-z": () =>
                            undo(this.outerView.state, this.outerView.dispatch),
                        "Mod-y": () =>
                            redo(this.outerView.state, this.outerView.dispatch),
                    }),
                ],
            }),
            dispatchTransaction: this.dispatchInner.bind(this),
            handleDOMEvents: {
                mousedown: () => {
                    // Keep focus in the inner editor while the outer view holds
                    // focus (clicking the footnote first selects the node).
                    if (this.outerView.hasFocus()) {
                        this.innerView?.focus();
                    }

                    return false;
                },
            },
        });

        // Register this inner view so toolbar style commands target its
        // selection instead of the outer NodeSelection over the whole footnote.
        setActiveFootnoteView(this.innerView);
    }

    close() {
        if (this.innerView) {
            clearActiveFootnoteView(this.innerView);
        }

        this.innerView?.destroy();
        this.innerView = null;
        this.dom.textContent = "";
    }

    dispatchInner(tr: Transaction) {
        if (!this.innerView) {
            return;
        }

        const { state, transactions } =
            this.innerView.state.applyTransaction(tr);
        this.innerView.updateState(state);

        if (tr.getMeta("fromOutside")) {
            return;
        }

        const pos = this.getPos();

        if (pos == null) {
            return;
        }

        const outerTr = this.outerView.state.tr;
        const offsetMap = StepMap.offset(pos + 1);

        for (const transaction of transactions) {
            for (const step of transaction.steps) {
                const mapped = step.map(offsetMap);

                if (mapped) {
                    outerTr.step(mapped);
                }
            }
        }

        if (outerTr.docChanged) {
            this.outerView.dispatch(outerTr);
        }
    }

    update(node: ProseMirrorNode) {
        if (!node.sameMarkup(this.node)) {
            return false;
        }

        this.node = node;

        if (this.innerView) {
            const { state } = this.innerView;
            const start = node.content.findDiffStart(state.doc.content);

            if (start != null) {
                const diffEnd = node.content.findDiffEnd(state.doc.content);

                if (diffEnd) {
                    let { a: endA, b: endB } = diffEnd;
                    const overlap = start - Math.min(endA, endB);

                    if (overlap > 0) {
                        endA += overlap;
                        endB += overlap;
                    }

                    this.innerView.dispatch(
                        state.tr
                            .replace(start, endB, node.slice(start, endA))
                            .setMeta("fromOutside", true),
                    );
                }
            }
        }

        return true;
    }

    destroy() {
        if (this.innerView) {
            this.close();
        }
    }

    stopEvent(event: Event) {
        return Boolean(
            this.innerView &&
            event.target instanceof globalThis.Node &&
            this.innerView.dom.contains(event.target),
        );
    }

    ignoreMutation() {
        return true;
    }
}

export const FootnoteExtension = Node.create({
    name: "footnote",
    // Above the WJtags HTML-preservation extensions (priority 1000) so the
    // <footnote> tag is parsed into this node, not a generic preserved tag.
    priority: 1100,
    group: "inline",
    content: "text*",
    inline: true,
    atom: true,
    draggable: true,

    // Rust parser emits <footnote>…</footnote>.
    parseHTML() {
        return [{ tag: "footnote" }];
    },

    // Serialization (CodeView / copy) and the fallback element; the live editor
    // uses the node view below.
    renderHTML({ HTMLAttributes }) {
        return ["footnote", mergeAttributes(HTMLAttributes), 0];
    },

    addNodeView() {
        return (({ node, editor, getPos }: NodeViewRendererProps) =>
            new FootnoteView(
                node,
                editor.view,
                getPos as () => number | undefined,
            )) as unknown as NodeViewRenderer;
    },

    addCommands() {
        return {
            insertFootnote:
                () =>
                ({ state, dispatch }) => {
                    const { from } = state.selection;
                    const node = this.type.create();

                    if (dispatch) {
                        const tr = state.tr.replaceSelectionWith(node);
                        // Select the freshly inserted footnote so the editing
                        // tooltip opens immediately.
                        tr.setSelection(NodeSelection.create(tr.doc, from));
                        dispatch(tr.scrollIntoView());
                    }

                    return true;
                },
        };
    },
});
