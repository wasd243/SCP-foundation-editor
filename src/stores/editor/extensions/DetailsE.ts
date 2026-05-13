// DetailE.ts is a collapsible block extension for Tiptap
import { findParentNode } from "@tiptap/core";
import { Details, DetailsSummary } from "@tiptap/extension-details";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { Plugin, type Selection } from "@tiptap/pm/state";

function getSummaryText(summary: ProseMirrorNode) {
    return summary.textContent;
}

function getSummaryDeletionRange(
    summary: ProseMirrorNode,
    summaryPos: number,
    selection: Selection,
    key: "Backspace" | "Delete",
) {
    const summaryStart = summaryPos + 1;
    const summaryEnd = summaryPos + summary.nodeSize - 1;

    if (!selection.empty) {
        const from = Math.max(selection.from, summaryStart);
        const to = Math.min(selection.to, summaryEnd);

        return from < to ? { from, to } : null;
    }

    const cursor = selection.from;

    if (key === "Backspace") {
        return cursor > summaryStart ? { from: cursor - 1, to: cursor } : null;
    }

    return cursor < summaryEnd ? { from: cursor, to: cursor + 1 } : null;
}

function summaryDeletionLeavesEmptyText(
    summary: ProseMirrorNode,
    summaryPos: number,
    deletionRange: { from: number; to: number },
) {
    const summaryStart = summaryPos + 1;
    let text = "";
    let deletedText = false;

    summary.descendants((child, offset) => {
        if (!child.isText) {
            return true;
        }

        const childText = child.text ?? "";

        for (let index = 0; index < childText.length; index += 1) {
            const charFrom = summaryStart + offset + index;
            const charTo = charFrom + 1;
            const isDeleted = charFrom >= deletionRange.from && charTo <= deletionRange.to;

            if (isDeleted) {
                deletedText = true;
                continue;
            }

            text += childText[index];
        }

        return true;
    });

    return deletedText && text.length === 0;
}

function countNestedDetails(node: ProseMirrorNode, hasDetailsAncestor = false): number {
    let nestedDetailsCount = 0;

    node.forEach(child => {
        const isDetailsNode = child.type.name === "details";

        if (isDetailsNode && hasDetailsAncestor) {
            nestedDetailsCount += 1;
        }

        if (child.childCount > 0) {
            nestedDetailsCount += countNestedDetails(child, hasDetailsAncestor || isDetailsNode);
        }
    });

    return nestedDetailsCount;
}

// Details Extension for collapsible blocks
export const DetailsExtension = Details.extend({
    selectable: false,

    addProseMirrorPlugins() {
        const parentPlugins = this.parent?.() ?? [];

        return [
            ...parentPlugins,
            new Plugin({
                filterTransaction: (transaction, state) => {
                    if (!transaction.docChanged) {
                        return true;
                    }

                    const previousNestedDetailsCount = countNestedDetails(state.doc);
                    const nextNestedDetailsCount = countNestedDetails(transaction.doc);

                    return nextNestedDetailsCount <= previousNestedDetailsCount;
                },
            }),
        ];
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

            const { $from, empty } = selection;
            const summaryStart = detailsSummary.pos + 1;
            const summaryEnd = detailsSummary.pos + detailsSummary.node.nodeSize - 1;
            const atBoundary = empty && (key === "Backspace" ? $from.pos === summaryStart : $from.pos === summaryEnd);
            const details = findParentNode(node => node.type.name === "details")(selection);

            if (!details) {
                return true;
            }

            const deleteDetails = () => {
                const paragraph = state.schema.nodes.paragraph?.createAndFill();
                const transaction = state.doc.childCount === 1 && paragraph
                    ? state.tr.replaceWith(details.pos, details.pos + details.node.nodeSize, paragraph)
                    : state.tr.delete(details.pos, details.pos + details.node.nodeSize);

                transaction.scrollIntoView();
                view.dispatch(transaction);

                return true;
            };

            const deletionRange = getSummaryDeletionRange(detailsSummary.node, detailsSummary.pos, selection, key);

            if (deletionRange && summaryDeletionLeavesEmptyText(detailsSummary.node, detailsSummary.pos, deletionRange)) {
                return deleteDetails();
            }

            if (getSummaryText(detailsSummary.node).length > 0) {
                return atBoundary;
            }

            return deleteDetails();
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
