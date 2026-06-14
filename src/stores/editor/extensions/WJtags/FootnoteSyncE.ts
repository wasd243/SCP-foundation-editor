// `FootnoteSyncE.ts` is a plugin that synchronizes footnote content from `[[footnoteblock]]` to `wj-footnote` elements.

import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { Plugin, PluginKey, TextSelection } from "@tiptap/pm/state";

import {
    collectFootnoteDocumentInfo,
    ensureFootnoteListLeadingBlankLine,
    findClosestEmptyFootnoteContentsSelection,
    getDeletedFootnoteRefKeys,
    getFootnoteListItemDeletionRanges,
    getFootnoteListItemRepairs,
    renumberFootnotes,
    type FootnoteContentNode,
} from "./FootnoteE";

export function createFootnoteSyncPlugin() {
    return new Plugin({
        key: new PluginKey("wjFootnoteSync"),
        appendTransaction(transactions, oldState, newState) {
            if (!transactions.some((transaction) => transaction.docChanged)) {
                return null;
            }

            const footnoteListItemRepairs = getFootnoteListItemRepairs(
                newState.doc,
            );

            if (footnoteListItemRepairs.length > 0) {
                const transaction = newState.tr;

                footnoteListItemRepairs.forEach((repair) => {
                    if (repair.type === "replace") {
                        transaction.replaceWith(
                            repair.from,
                            repair.to,
                            repair.node,
                        );
                        return;
                    }

                    transaction.insert(repair.pos, repair.node);
                });

                const selectionPos = findClosestEmptyFootnoteContentsSelection(
                    transaction.doc,
                    transaction.selection.from,
                );

                if (selectionPos !== null) {
                    try {
                        transaction.setSelection(
                            TextSelection.create(transaction.doc, selectionPos),
                        );
                    } catch {
                        // Keep ProseMirror's mapped selection if the browser produced an invalid edge position.
                    }
                }

                ensureFootnoteListLeadingBlankLine(transaction);

                return transaction;
            }

            const newFootnoteInfo = collectFootnoteDocumentInfo(newState.doc);
            const deletedRefKeys = getDeletedFootnoteRefKeys(
                oldState.doc,
                newState.doc,
            );
            const deletionRanges = getFootnoteListItemDeletionRanges(
                newFootnoteInfo.listItems,
                deletedRefKeys,
            );

            if (deletionRanges.length > 0) {
                const transaction = newState.tr;

                deletionRanges.forEach((range) => {
                    transaction.delete(range.from, range.to);
                });

                renumberFootnotes(transaction);
                ensureFootnoteListLeadingBlankLine(transaction);

                return transaction;
            }

            const renumberTransaction = newState.tr;

            if (
                renumberFootnotes(renumberTransaction) ||
                ensureFootnoteListLeadingBlankLine(renumberTransaction)
            ) {
                return renumberTransaction;
            }

            const { sources, targets } = newFootnoteInfo;

            if (sources.length === 0 || targets.length === 0) {
                return null;
            }

            const sourceByKey = new Map<string, FootnoteContentNode>();
            sources.forEach((source) => {
                if (source.key && !sourceByKey.has(source.key)) {
                    sourceByKey.set(source.key, source);
                }
            });

            const transaction = newState.tr;
            let changed = false;

            [...targets]
                .sort((left, right) => right.pos - left.pos)
                .forEach((target, targetIndexFromEnd) => {
                    const targetIndex = targets.length - 1 - targetIndexFromEnd;
                    const source = target.key
                        ? sourceByKey.get(target.key)
                        : sources[targetIndex];

                    if (
                        !source ||
                        target.node.content.eq(source.node.content)
                    ) {
                        return;
                    }

                    transaction.replaceWith(
                        target.pos + 1,
                        target.pos + target.node.nodeSize - 1,
                        source.node.content,
                    );
                    changed = true;
                });

            if (!changed && !ensureFootnoteListLeadingBlankLine(transaction)) {
                return null;
            }

            return transaction;
        },
    });
}
