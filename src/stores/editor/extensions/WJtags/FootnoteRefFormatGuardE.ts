import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import type { ResolvedPos } from "@tiptap/pm/model";
import { Plugin, PluginKey } from "@tiptap/pm/state";
import type { Transaction } from "@tiptap/pm/state";

import { nodeHasClass } from "./htmlPreserveE";

const footnoteRefClass = "wj-footnote-ref";
const footnoteRefContentsClass = "wj-footnote-ref-contents";

const marksBlockedInsideFootnoteRef = new Set([
    "fontSize",
    "bold",
    "italic",
    "underline",
    "strike",
    "textColor",
    "link",
    "subscript",
    "superscript",
]);

function isFootnoteRefNode(node: ProseMirrorNode) {
    return nodeHasClass(node, footnoteRefClass);
}

export function isInsideFootnoteRef($pos: ResolvedPos) {
    for (let depth = $pos.depth; depth > 0; depth -= 1) {
        if (isFootnoteRefNode($pos.node(depth))) {
            return true;
        }
    }

    return false;
}

function isInsideFootnoteRefContents($pos: ResolvedPos) {
    for (let depth = $pos.depth; depth > 0; depth -= 1) {
        if (nodeHasClass($pos.node(depth), footnoteRefContentsClass)) {
            return true;
        }
    }

    return false;
}

function removeBlockedMarksInFootnoteRefs(transaction: Transaction) {
    const { doc } = transaction;
    let changed = false;

    doc.descendants((node, pos) => {
        if (!node.isText || node.marks.length === 0) {
            return;
        }

        const $pos = doc.resolve(pos);

        if (!isInsideFootnoteRef($pos) || isInsideFootnoteRefContents($pos)) {
            return;
        }

        node.marks.forEach((mark) => {
            if (!marksBlockedInsideFootnoteRef.has(mark.type.name)) {
                return;
            }

            transaction.removeMark(pos, pos + node.nodeSize, mark.type);
            changed = true;
        });
    });

    return changed;
}

export function createFootnoteRefFormatGuardPlugin() {
    return new Plugin({
        key: new PluginKey("wjFootnoteRefFormatGuard"),
        appendTransaction(transactions, _oldState, newState) {
            if (!transactions.some((transaction) => transaction.docChanged)) {
                return null;
            }

            const transaction = newState.tr;

            if (!removeBlockedMarksInFootnoteRefs(transaction)) {
                return null;
            }

            return transaction;
        },
    });
}
