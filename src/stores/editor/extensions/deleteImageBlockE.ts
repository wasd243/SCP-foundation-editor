import type { Node as ProseMirrorNode, ResolvedPos } from "@tiptap/pm/model";
import { Plugin, PluginKey } from "@tiptap/pm/state";

import { getNodeAttribute, nodeHasClass } from "./WJtags/htmlPreserveE";

type PositionedNode = {
    node: ProseMirrorNode;
    pos: number;
};

const imageBlockIncludeName = "component:image-block";
const imageBlockGuardKey = new PluginKey("imageBlockGuard");

function isImageBlockNode(node: ProseMirrorNode) {
    return nodeHasClass(node, "image-container") &&
        getNodeAttribute(node, "data-editor-include") === imageBlockIncludeName;
}

function isImageCaptionNode(node: ProseMirrorNode) {
    return nodeHasClass(node, "scp-image-caption");
}

function isImageNode(node: ProseMirrorNode) {
    return node.type.name === "image";
}

function hasDescendant(node: ProseMirrorNode, predicate: (node: ProseMirrorNode) => boolean) {
    let found = false;

    node.descendants(child => {
        if (predicate(child)) {
            found = true;
            return false;
        }

        return true;
    });

    return found;
}

function hasImage(node: ProseMirrorNode) {
    return hasDescendant(node, isImageNode);
}

function hasCaption(node: ProseMirrorNode) {
    return hasDescendant(node, isImageCaptionNode);
}

function findAncestor($pos: ResolvedPos, predicate: (node: ProseMirrorNode) => boolean): PositionedNode | null {
    for (let depth = $pos.depth; depth > 0; depth -= 1) {
        const node = $pos.node(depth);

        if (predicate(node)) {
            return {
                node,
                pos: $pos.before(depth),
            };
        }
    }

    return null;
}

function findCaptionAncestor($pos: ResolvedPos) {
    return findAncestor($pos, isImageCaptionNode);
}

function selectionStartsAtCaptionBoundary($pos: ResolvedPos, caption: PositionedNode) {
    return $pos.pos === caption.pos + 1;
}

function selectionEndsAtCaptionBoundary($pos: ResolvedPos, caption: PositionedNode) {
    return $pos.pos === caption.pos + caption.node.nodeSize - 1;
}

function shouldBlockCaptionBoundaryDelete(key: "Backspace" | "Delete", $pos: ResolvedPos) {
    const caption = findCaptionAncestor($pos);

    if (!caption) return false;

    return key === "Backspace"
        ? selectionStartsAtCaptionBoundary($pos, caption)
        : selectionEndsAtCaptionBoundary($pos, caption);
}

function hasInvalidImageBlockWithoutCaption(doc: ProseMirrorNode) {
    let invalid = false;

    doc.descendants(node => {
        if (!isImageBlockNode(node)) {
            return true;
        }

        if (hasImage(node) && !hasCaption(node)) {
            invalid = true;
            return false;
        }

        return false;
    });

    return invalid;
}

function getImageBlocksWithoutImages(doc: ProseMirrorNode) {
    const ranges: PositionedNode[] = [];

    doc.descendants((node, pos) => {
        if (!isImageBlockNode(node)) {
            return true;
        }

        if (!hasImage(node)) {
            ranges.push({ node, pos });
        }

        return false;
    });

    return ranges.sort((left, right) => right.pos - left.pos);
}

function isSelectionInsideCaption($from: ResolvedPos, $to: ResolvedPos) {
    return Boolean(findCaptionAncestor($from) && findCaptionAncestor($to));
}

function normalizeCaptionPaste(text: string) {
    return text.replace(/\s*\r?\n\s*/g, " ");
}

export function createDeleteImageBlockPlugin() {
    return new Plugin({
        key: imageBlockGuardKey,
        filterTransaction(transaction) {
            if (!transaction.docChanged) {
                return true;
            }

            return !hasInvalidImageBlockWithoutCaption(transaction.doc);
        },
        appendTransaction(transactions, _oldState, newState) {
            if (!transactions.some(transaction => transaction.docChanged)) {
                return null;
            }

            const imageBlocksWithoutImages = getImageBlocksWithoutImages(newState.doc);

            if (imageBlocksWithoutImages.length === 0) {
                return null;
            }

            const transaction = newState.tr;

            imageBlocksWithoutImages.forEach(({ node, pos }) => {
                transaction.delete(pos, pos + node.nodeSize);
            });

            return transaction;
        },
        props: {
            handleKeyDown(view, event) {
                if (event.key === "Enter" && isSelectionInsideCaption(view.state.selection.$from, view.state.selection.$to)) {
                    event.preventDefault();
                    return true;
                }

                if (
                    (event.key === "Backspace" || event.key === "Delete") &&
                    view.state.selection.empty &&
                    shouldBlockCaptionBoundaryDelete(event.key, view.state.selection.$from)
                ) {
                    event.preventDefault();
                    return true;
                }

                return false;
            },
            handlePaste(view, event) {
                if (!isSelectionInsideCaption(view.state.selection.$from, view.state.selection.$to)) {
                    return false;
                }

                const text = event.clipboardData?.getData("text/plain") ?? "";

                if (!/\r?\n/.test(text)) {
                    return false;
                }

                event.preventDefault();
                view.dispatch(view.state.tr.insertText(normalizeCaptionPaste(text)));

                return true;
            },
        },
    });
}
