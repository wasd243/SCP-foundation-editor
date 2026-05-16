import type { Node as ProseMirrorNode } from "@tiptap/pm/model";

import {
    getNodeAttribute,
    getNodeClassAttribute,
    getNodeHTMLAttributes,
    getNodeTagName,
    nodeHasClass,
    removeHTMLAttribute,
    type HTMLAttributes,
} from "./htmlPreserveE";

const footnoteKeyAttributes = [
    "data-footnote-id",
    "footnote-id",
    "data-id",
    "id",
    "href",
];

export type FootnoteSyncContext = {
    listItemKey: string | null;
    refKey: string | null;
    parentListNode: ProseMirrorNode | null;
    parentListPos: number | null;
    parentListChildCount: number;
};

export type FootnoteContentNode = {
    node: ProseMirrorNode;
    pos: number;
    key: string | null;
};

export type FootnoteListItemNode = FootnoteContentNode & {
    parentListNode: ProseMirrorNode | null;
    parentListPos: number | null;
    parentListChildCount: number;
};

export type FootnoteDocumentInfo = {
    refKeys: Set<string>;
    sources: FootnoteContentNode[];
    targets: FootnoteContentNode[];
    listItems: FootnoteListItemNode[];
};

export type FootnoteListItemRepair =
    | { type: "replace"; from: number; to: number; node: ProseMirrorNode }
    | { type: "insert"; pos: number; node: ProseMirrorNode };

function sanitizeFootnoteContentsNode(node: ProseMirrorNode) {
    return node.type.create(
        removeHTMLAttribute(node, "contenteditable"),
        node.content,
        node.marks,
    );
}

function normalizeFootnoteKey(value: string | null): string | null {
    if (!value) return null;

    const trimmed = value.trim();
    if (!trimmed) return null;

    return trimmed.replace(/^#/, "");
}

function getFootnoteKey(node: ProseMirrorNode): string | null {
    for (const attribute of footnoteKeyAttributes) {
        const key = normalizeFootnoteKey(getNodeAttribute(node, attribute));
        if (key) return key;
    }

    return null;
}

function findDescendantFootnoteKey(node: ProseMirrorNode, className: string): string | null {
    let key: string | null = null;

    node.descendants(child => {
        if (!nodeHasClass(child, className)) {
            return true;
        }

        key = getFootnoteKey(child);

        return !key;
    });

    return key;
}

function normalizeFootnoteMarkerText(text: string) {
    return text.trim().replace(/\.$/, "");
}

function hasDescendantClass(node: ProseMirrorNode, className: string) {
    let found = false;

    node.descendants(child => {
        if (nodeHasClass(child, className)) {
            found = true;
            return false;
        }

        return true;
    });

    return found;
}

function hasBlockFootnoteContentsNode(node: ProseMirrorNode) {
    let found = false;

    node.descendants(child => {
        if (nodeHasClass(child, "wj-footnote-list-item-contents") && !child.isInline) {
            found = true;
            return false;
        }

        return true;
    });

    return found;
}

function isFootnoteListChromeNode(node: ProseMirrorNode) {
    return nodeHasClass(node, "wj-footnote-list-item-marker") ||
        nodeHasClass(node, "wj-footnote-sep");
}

function isMeaningfulLooseText(node: ProseMirrorNode) {
    return node.isText && node.textContent.length > 0;
}

function hasLooseFootnoteListItemContent(node: ProseMirrorNode) {
    let found = false;

    node.forEach(child => {
        if (found) return;
        if (nodeHasClass(child, "wj-footnote-list-item-contents")) return;
        if (isFootnoteListChromeNode(child)) return;
        if (isMeaningfulLooseText(child) || child.isInline) {
            found = true;
        }
    });

    return found;
}

function createEmptyFootnoteContentsNode(schema: ProseMirrorNode["type"]["schema"]) {
    const inlineTag = schema.nodes.wjInlineTag;

    if (!inlineTag) return null;

    return inlineTag.create({
        tagName: "span",
        htmlAttributes: {
            class: "wj-footnote-list-item-contents",
        },
    });
}

function createFootnoteContentsNode(
    schema: ProseMirrorNode["type"]["schema"],
    sourceNode: ProseMirrorNode,
    content: ProseMirrorNode[],
) {
    const inlineTag = schema.nodes.wjInlineTag;

    if (!inlineTag) return null;

    const htmlAttributes = {
        ...getNodeHTMLAttributes(sourceNode),
        class: getNodeClassAttribute(sourceNode) || "wj-footnote-list-item-contents",
    } as HTMLAttributes;

    delete htmlAttributes.contenteditable;

    return inlineTag.create({
        tagName: "span",
        htmlAttributes,
    }, content);
}

function findFootnoteContentsNode(node: ProseMirrorNode) {
    let contentsNode: ProseMirrorNode | null = null;

    node.descendants(child => {
        if (!nodeHasClass(child, "wj-footnote-list-item-contents")) {
            return true;
        }

        contentsNode = child;
        return false;
    });

    return contentsNode;
}

function collectFootnoteChromeNodes(node: ProseMirrorNode, output: ProseMirrorNode[]) {
    node.forEach(child => {
        if (nodeHasClass(child, "wj-footnote-list-item-contents")) {
            return;
        }

        if (isFootnoteListChromeNode(child)) {
            output.push(child);
            return;
        }

        if (!child.isInline) {
            collectFootnoteChromeNodes(child, output);
        }
    });
}

function collectFootnoteBodyInlineNodes(node: ProseMirrorNode, output: ProseMirrorNode[]) {
    node.forEach(child => {
        if (nodeHasClass(child, "wj-footnote-list-item-contents")) {
            collectFootnoteBodyInlineNodes(child, output);
            return;
        }

        if (isFootnoteListChromeNode(child)) {
            return;
        }

        if (child.isText || child.isInline) {
            output.push(child);
            return;
        }

        collectFootnoteBodyInlineNodes(child, output);
    });
}

function createFootnoteListItemNode(schema: ProseMirrorNode["type"]["schema"], node: ProseMirrorNode) {
    const textBlockTag = schema.nodes.wjTextBlockTag;

    if (!textBlockTag) return null;

    const content: ProseMirrorNode[] = [];
    const bodyContent: ProseMirrorNode[] = [];
    const sourceContentsNode = findFootnoteContentsNode(node);

    collectFootnoteChromeNodes(node, content);
    collectFootnoteBodyInlineNodes(node, bodyContent);

    const contentsNode = sourceContentsNode
        ? createFootnoteContentsNode(schema, sourceContentsNode, bodyContent)
        : createEmptyFootnoteContentsNode(schema);

    if (contentsNode) {
        content.push(contentsNode);
    }

    return textBlockTag.create({
        tagName: "li",
        htmlAttributes: getNodeHTMLAttributes(node),
    }, content);
}

export function getFootnoteListItemRepairs(doc: ProseMirrorNode) {
    const repairs: FootnoteListItemRepair[] = [];
    const schema = doc.type.schema;

    doc.descendants((node, pos) => {
        if (!nodeHasClass(node, "wj-footnote-list-item")) {
            return true;
        }

        const shouldReplace =
            node.type.name !== "wjTextBlockTag" ||
            getNodeTagName(node) !== "li" ||
            hasBlockFootnoteContentsNode(node) ||
            hasLooseFootnoteListItemContent(node);

        if (shouldReplace) {
            const replacement = createFootnoteListItemNode(schema, node);

            if (replacement) {
                repairs.push({
                    type: "replace",
                    from: pos,
                    to: pos + node.nodeSize,
                    node: replacement,
                });
            }

            return false;
        }

        if (!hasDescendantClass(node, "wj-footnote-list-item-contents")) {
            const emptyContents = createEmptyFootnoteContentsNode(schema);

            if (emptyContents) {
                repairs.push({
                    type: "insert",
                    pos: pos + node.nodeSize - 1,
                    node: emptyContents,
                });
            }
        }

        return false;
    });

    return repairs.sort((left, right) => {
        const leftPos = left.type === "replace" ? left.from : left.pos;
        const rightPos = right.type === "replace" ? right.from : right.pos;

        return rightPos - leftPos;
    });
}

export function findClosestEmptyFootnoteContentsSelection(doc: ProseMirrorNode, pos: number) {
    let closestDistance = Number.POSITIVE_INFINITY;
    let closestPos: number | null = null;

    doc.descendants((node, nodePos) => {
        if (!nodeHasClass(node, "wj-footnote-list-item-contents")) {
            return true;
        }

        if (node.content.size > 0) {
            return false;
        }

        const selectionPos = nodePos + 1;
        const distance = Math.abs(selectionPos - pos);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestPos = selectionPos;
        }

        return false;
    });

    return closestPos;
}

function findDescendantFootnoteText(node: ProseMirrorNode, className: string): string | null {
    let text: string | null = null;

    node.descendants(child => {
        if (!nodeHasClass(child, className)) {
            return true;
        }

        text = normalizeFootnoteMarkerText(child.textContent);

        return !text;
    });

    return text;
}

function getFootnoteKeyFromMarker(node: ProseMirrorNode, markerClassName: string): string | null {
    return (
        getFootnoteKey(node) ??
        findDescendantFootnoteKey(node, markerClassName) ??
        findDescendantFootnoteText(node, markerClassName)
    );
}

function getOwnFootnoteMarkerKey(node: ProseMirrorNode): string | null {
    return getFootnoteKey(node) ?? normalizeFootnoteMarkerText(node.textContent);
}

function collectFootnoteContentNodes(
    node: ProseMirrorNode,
    pos: number,
    context: FootnoteSyncContext,
    info: FootnoteDocumentInfo,
) {
    const currentContext = { ...context };

    if (node.type.name === "orderedList" || getNodeTagName(node) === "ol") {
        currentContext.parentListNode = node;
        currentContext.parentListPos = pos;
        currentContext.parentListChildCount = node.childCount;
    }

    if (nodeHasClass(node, "wj-footnote-list-item")) {
        const listItemKey = getFootnoteKeyFromMarker(node, "wj-footnote-list-item-marker");

        currentContext.listItemKey = listItemKey ?? currentContext.listItemKey;

        info.listItems.push({
            node,
            pos,
            key: listItemKey,
            parentListNode: currentContext.parentListNode,
            parentListPos: currentContext.parentListPos,
            parentListChildCount: currentContext.parentListChildCount,
        });
    }

    if (nodeHasClass(node, "wj-footnote-ref")) {
        currentContext.refKey =
            getFootnoteKeyFromMarker(node, "wj-footnote-ref-marker") ??
            currentContext.refKey;
    }

    if (nodeHasClass(node, "wj-footnote-ref-marker")) {
        const markerKey = getOwnFootnoteMarkerKey(node);

        if (markerKey) {
            info.refKeys.add(markerKey);
        }
    }

    if (nodeHasClass(node, "wj-footnote-list-item-contents")) {
        info.sources.push({
            node,
            pos,
            key: getFootnoteKey(node) ?? currentContext.listItemKey,
        });
    }

    if (nodeHasClass(node, "wj-footnote-ref-contents")) {
        info.targets.push({
            node,
            pos,
            key: getFootnoteKey(node) ?? currentContext.refKey,
        });
    }

    node.forEach((child, offset) => {
        const childPos = pos + 1 + offset;

        collectFootnoteContentNodes(child, childPos, currentContext, info);
    });
}

export function collectFootnoteDocumentInfo(doc: ProseMirrorNode): FootnoteDocumentInfo {
    const info: FootnoteDocumentInfo = {
        refKeys: new Set(),
        sources: [],
        targets: [],
        listItems: [],
    };

    collectFootnoteContentNodes(
        doc,
        -1,
        {
            listItemKey: null,
            refKey: null,
            parentListNode: null,
            parentListPos: null,
            parentListChildCount: 0,
        },
        info,
    );

    return info;
}

export function getDeletedFootnoteRefKeys(oldDoc: ProseMirrorNode, newDoc: ProseMirrorNode) {
    const oldRefKeys = collectFootnoteDocumentInfo(oldDoc).refKeys;
    const newRefKeys = collectFootnoteDocumentInfo(newDoc).refKeys;

    return Array.from(oldRefKeys).filter(key => !newRefKeys.has(key));
}

export function getFootnoteListItemDeletionRanges(listItems: FootnoteListItemNode[], deletedRefKeys: string[]) {
    const deletedKeySet = new Set(deletedRefKeys);
    const itemsToDelete = listItems.filter(item => item.key && deletedKeySet.has(item.key));
    const itemsByParentList = new Map<number, FootnoteListItemNode[]>();
    const ranges: Array<{ from: number; to: number }> = [];

    itemsToDelete.forEach(item => {
        if (item.parentListPos === null) {
            ranges.push({ from: item.pos, to: item.pos + item.node.nodeSize });
            return;
        }

        const siblings = itemsByParentList.get(item.parentListPos) ?? [];
        siblings.push(item);
        itemsByParentList.set(item.parentListPos, siblings);
    });

    itemsByParentList.forEach(siblings => {
        const [firstSibling] = siblings;

        if (
            firstSibling.parentListNode &&
            firstSibling.parentListPos !== null &&
            siblings.length >= firstSibling.parentListChildCount
        ) {
            ranges.push({
                from: firstSibling.parentListPos,
                to: firstSibling.parentListPos + firstSibling.parentListNode.nodeSize,
            });
            return;
        }

        siblings.forEach(item => {
            ranges.push({ from: item.pos, to: item.pos + item.node.nodeSize });
        });
    });

    return ranges.sort((left, right) => right.from - left.from);
}
