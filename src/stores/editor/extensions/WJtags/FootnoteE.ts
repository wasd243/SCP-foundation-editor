import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import type { Transaction } from "@tiptap/pm/state";

import {
    getNodeAttribute,
    getNodeClassAttribute,
    getNodeHTMLAttributes,
    getNodeTagName,
    nodeHasClass,
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

type FootnoteRenumberContext = {
    listItemKey: string | null;
    refKey: string | null;
};

type FootnoteRenumberOperation =
    | { type: "replace"; from: number; to: number; node: ProseMirrorNode }
    | { type: "setNodeMarkup"; pos: number; node: ProseMirrorNode; attrs: Record<string, unknown> };

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

function setNodeHTMLAttributes(node: ProseMirrorNode, attributes: HTMLAttributes) {
    const htmlAttributes = {
        ...getNodeHTMLAttributes(node),
        ...attributes,
    };

    if (node.attrs.htmlAttributes && typeof node.attrs.htmlAttributes === "object") {
        return {
            ...node.attrs,
            htmlAttributes,
        };
    }

    return {
        ...node.attrs,
        ...htmlAttributes,
    };
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

// This function is used when Prose Mirror changes footnote edit area into normal <p></p> text
// Do not delete this function unless Prose Mirror would not change contenteditable type
// ---------------------------------------------------------------------------------------------------------------------
// if the user deletes all texts in the footnote edit area, Prose Mirror would change it into <p></p>
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
            contenteditable: "false",
        },
    });
}

function createFootnoteSeparatorNode(schema: ProseMirrorNode["type"]["schema"], sourceNode: ProseMirrorNode | null) {
    const inlineTag = schema.nodes.wjInlineTag;

    if (!inlineTag) return null;

    const htmlAttributes = sourceNode
        ? {
            ...getNodeHTMLAttributes(sourceNode),
            class: getNodeClassAttribute(sourceNode) || "wj-footnote-sep",
        } as HTMLAttributes
        : { class: "wj-footnote-sep" };

    return inlineTag.create({
        tagName: "span",
        htmlAttributes,
    }, [schema.text(".")]);
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

function findFootnoteSeparatorNode(node: ProseMirrorNode) {
    let separatorNode: ProseMirrorNode | null = null;

    node.descendants(child => {
        if (!nodeHasClass(child, "wj-footnote-sep")) {
            return true;
        }

        separatorNode = child;
        return false;
    });

    return separatorNode;
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

function createFootnoteNumberingMap(doc: ProseMirrorNode) {
    const numberingMap = new Map<string, string>();

    doc.descendants(node => {
        if (!nodeHasClass(node, "wj-footnote-ref")) {
            return true;
        }

        const key = getFootnoteKeyFromMarker(node, "wj-footnote-ref-marker");

        if (key && !numberingMap.has(key)) {
            numberingMap.set(key, String(numberingMap.size + 1));
        }

        return false;
    });

    if (numberingMap.size > 0) {
        return numberingMap;
    }

    doc.descendants(node => {
        if (!nodeHasClass(node, "wj-footnote-list-item")) {
            return true;
        }

        const key = getFootnoteKeyFromMarker(node, "wj-footnote-list-item-marker");

        if (key && !numberingMap.has(key)) {
            numberingMap.set(key, String(numberingMap.size + 1));
        }

        return false;
    });

    return numberingMap;
}

function createTextOnlyNode(node: ProseMirrorNode, text: string) {
    return node.type.create(node.attrs, [node.type.schema.text(text)], node.marks);
}

function createFootnoteRefMarkerNode(node: ProseMirrorNode, footnoteId: string) {
    const attrs = setNodeHTMLAttributes(node, {
        "aria-label": `Footnote ${footnoteId}.`,
        "data-id": footnoteId,
    });

    return node.type.create(attrs, [node.type.schema.text(footnoteId)], node.marks);
}

function createFootnoteListMarkerNode(node: ProseMirrorNode, footnoteId: string) {
    const separatorNode = createFootnoteSeparatorNode(node.type.schema, findFootnoteSeparatorNode(node));
    const content = separatorNode
        ? [node.type.schema.text(footnoteId), separatorNode]
        : [node.type.schema.text(footnoteId)];

    return node.type.create(node.attrs, content, node.marks);
}

function maybePushReplacement(
    operations: FootnoteRenumberOperation[],
    node: ProseMirrorNode,
    pos: number,
    replacement: ProseMirrorNode,
) {
    if (node.eq(replacement)) {
        return;
    }

    operations.push({
        type: "replace",
        from: pos,
        to: pos + node.nodeSize,
        node: replacement,
    });
}

function maybePushAttributeUpdate(
    operations: FootnoteRenumberOperation[],
    node: ProseMirrorNode,
    pos: number,
    attributes: HTMLAttributes,
) {
    if (Object.entries(attributes).every(([name, value]) => getNodeAttribute(node, name) === value)) {
        return;
    }

    operations.push({
        type: "setNodeMarkup",
        pos,
        node,
        attrs: setNodeHTMLAttributes(node, attributes),
    });
}

function collectFootnoteRenumberOperations(
    node: ProseMirrorNode,
    pos: number,
    numberingMap: Map<string, string>,
    context: FootnoteRenumberContext,
    operations: FootnoteRenumberOperation[],
) {
    const currentContext = { ...context };

    if (nodeHasClass(node, "wj-footnote-ref")) {
        currentContext.refKey =
            getFootnoteKeyFromMarker(node, "wj-footnote-ref-marker") ??
            currentContext.refKey;
    }

    if (nodeHasClass(node, "wj-footnote-list-item")) {
        currentContext.listItemKey =
            getFootnoteKeyFromMarker(node, "wj-footnote-list-item-marker") ??
            currentContext.listItemKey;

        const nextListItemKey = currentContext.listItemKey
            ? numberingMap.get(currentContext.listItemKey)
            : null;

        if (nextListItemKey) {
            maybePushAttributeUpdate(operations, node, pos, { "data-id": nextListItemKey });
        }
    }

    if (nodeHasClass(node, "wj-footnote-ref-marker")) {
        const key = getOwnFootnoteMarkerKey(node) ?? currentContext.refKey;
        const nextRefKey = key ? numberingMap.get(key) : null;

        if (nextRefKey) {
            maybePushReplacement(operations, node, pos, createFootnoteRefMarkerNode(node, nextRefKey));
        }
    }

    if (nodeHasClass(node, "wj-footnote-ref-tooltip-label")) {
        const nextRefKey = currentContext.refKey ? numberingMap.get(currentContext.refKey) : null;

        if (nextRefKey) {
            maybePushReplacement(operations, node, pos, createTextOnlyNode(node, `Footnote ${nextRefKey}.`));
        }
    }

    if (nodeHasClass(node, "wj-footnote-list-item-marker")) {
        const key = getOwnFootnoteMarkerKey(node) ?? currentContext.listItemKey;
        const nextListItemKey = key ? numberingMap.get(key) : null;

        if (nextListItemKey) {
            maybePushReplacement(operations, node, pos, createFootnoteListMarkerNode(node, nextListItemKey));
        }
    }

    node.forEach((child, offset) => {
        collectFootnoteRenumberOperations(
            child,
            pos + offset + 1,
            numberingMap,
            currentContext,
            operations,
        );
    });
}

function getFootnoteRenumberOperations(doc: ProseMirrorNode) {
    const numberingMap = createFootnoteNumberingMap(doc);
    const operations: FootnoteRenumberOperation[] = [];

    if (numberingMap.size === 0) {
        return operations;
    }

    collectFootnoteRenumberOperations(
        doc,
        -1,
        numberingMap,
        {
            listItemKey: null,
            refKey: null,
        },
        operations,
    );

    return operations.sort((left, right) => {
        const leftPos = left.type === "replace" ? left.from : left.pos;
        const rightPos = right.type === "replace" ? right.from : right.pos;

        return rightPos - leftPos;
    });
}

export function renumberFootnotes(transaction: Transaction) {
    const operations = getFootnoteRenumberOperations(transaction.doc);

    operations.forEach(operation => {
        if (operation.type === "replace") {
            transaction.replaceWith(operation.from, operation.to, operation.node);
            return;
        }

        transaction.setNodeMarkup(operation.pos, undefined, operation.attrs, operation.node.marks);
    });

    return operations.length > 0;
}

function isEmptyParagraphNode(node: ProseMirrorNode) {
    return node.type.name === "paragraph" && node.textContent.trim().length === 0;
}

export function ensureFootnoteListLeadingBlankLine(transaction: Transaction) {
    const paragraphNode = transaction.doc.type.schema.nodes.paragraph;

    if (!paragraphNode) {
        return false;
    }

    let footnoteListPos: number | null = null;
    let previousNode: ProseMirrorNode | null = null;
    let offset = 0;

    for (let index = 0; index < transaction.doc.childCount; index += 1) {
        const child = transaction.doc.child(index);

        if (nodeHasClass(child, "wj-footnote-list")) {
            footnoteListPos = offset;
            break;
        }

        previousNode = child;
        offset += child.nodeSize;
    }

    if (footnoteListPos === null || (previousNode && isEmptyParagraphNode(previousNode))) {
        return false;
    }

    const blankParagraph = paragraphNode.createAndFill();

    if (!blankParagraph) {
        return false;
    }

    transaction.insert(footnoteListPos, blankParagraph);

    return true;
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
