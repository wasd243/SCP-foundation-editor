// WJtagsE.ts keeps Wikijump/FTML-generated HTML from being dropped by TipTap's schema.
import { Extension, Node } from "@tiptap/core";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import { Plugin, PluginKey } from "@tiptap/pm/state";

type HTMLAttributes = Record<string, string>;

const tiptapNativeTags = new Set([
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
]);

const blockTags = new Set([
    "address",
    "article",
    "aside",
    "blockquote",
    "dd",
    "details",
    "dialog",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
]);

const textBlockTags = new Set([
    "address",
    "article",
    "aside",
    "dd",
    "div",
    "dt",
    "figcaption",
    "footer",
    "header",
    "main",
    "nav",
    "section",
]);

const voidTags = new Set([
    "area",
    "base",
    "col",
    "embed",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]);

const ignoredRootTags = new Set([
    "body",
    "head",
    "html",
]);

const preservedGlobalAttributes = [
    "class",
    "id",
    "style",
    "role",
    "type",
    "data-id",
    "data-type",
    "aria-label",
    "aria-hidden",
    "aria-selected",
    "aria-controls",
    "aria-labelledby",
    "tabindex",
    "hidden",
];

const nativeAttributeTypes = [
    "paragraph",
    "heading",
    "blockquote",
    "orderedList",
    "bulletList",
    "listItem",
    "horizontalRule",
    "hardBreak",
    "codeBlock",
    "table",
    "tableRow",
    "tableCell",
    "tableHeader",
    "details",
    "detailsSummary",
    "detailsContent",
    "tabView",
    "tabViewButtonList",
    "tabViewButton",
    "tabViewPanelList",
    "tabViewPanel",
];

const footnoteKeyAttributes = [
    "data-footnote-id",
    "footnote-id",
    "data-id",
    "id",
    "href",
];

function getElementAttributes(element: HTMLElement): HTMLAttributes {
    return Object.fromEntries(
        Array.from(element.attributes).map(attribute => [attribute.name, attribute.value]),
    );
}

function isBlockElement(element: Element) {
    return blockTags.has(element.tagName.toLowerCase());
}

function hasBlockChild(element: HTMLElement) {
    return Array.from(element.children).some(isBlockElement);
}

function isNativeTipTapElement(element: HTMLElement) {
    return tiptapNativeTags.has(element.tagName.toLowerCase());
}

function shouldPreserveElement(element: HTMLElement) {
    const tagName = element.tagName.toLowerCase();

    if (ignoredRootTags.has(tagName)) return false;
    return !isNativeTipTapElement(element);


}

function shouldPreserveInlineElement(element: HTMLElement) {
    return shouldPreserveElement(element) && !isBlockElement(element) && !voidTags.has(element.tagName.toLowerCase());
}

function shouldPreserveVoidElement(element: HTMLElement) {
    return shouldPreserveElement(element) && voidTags.has(element.tagName.toLowerCase());
}

function shouldPreserveTextBlockElement(element: HTMLElement) {
    const tagName = element.tagName.toLowerCase();

    return shouldPreserveElement(element) && textBlockTags.has(tagName) && !hasBlockChild(element);
}

function shouldPreserveBlockElement(element: HTMLElement) {
    return shouldPreserveElement(element) && isBlockElement(element) && !shouldPreserveTextBlockElement(element);
}

function createAttributes() {
    return {
        tagName: {
            default: "div",
        },
        htmlAttributes: {
            default: {},
        },
    };
}

function parsePreservedElement(element: HTMLElement) {
    return {
        tagName: element.tagName.toLowerCase(),
        htmlAttributes: getElementAttributes(element),
    };
}

function renderPreservedElement({ node }: { node: ProseMirrorNode }) {
    const tagName = node.attrs.tagName as string;
    const htmlAttributes = node.attrs.htmlAttributes as HTMLAttributes;

    return [tagName, htmlAttributes, 0] as const;
}

function renderPreservedVoidElement({ node }: { node: ProseMirrorNode }) {
    const tagName = node.attrs.tagName as string;
    const htmlAttributes = node.attrs.htmlAttributes as HTMLAttributes;

    return [tagName, htmlAttributes] as const;
}

function getNodeHTMLAttributes(node: ProseMirrorNode): Record<string, unknown> {
    const htmlAttributes = node.attrs.htmlAttributes;

    if (htmlAttributes && typeof htmlAttributes === "object") {
        return htmlAttributes as Record<string, unknown>;
    }

    return node.attrs;
}

function getNodeAttribute(node: ProseMirrorNode, name: string): string | null {
    const attributes = getNodeHTMLAttributes(node);
    const value = attributes[name];

    return typeof value === "string" ? value : null;
}

function nodeHasClass(node: ProseMirrorNode, className: string) {
    const classAttribute = getNodeAttribute(node, "class");

    return classAttribute?.split(/\s+/).includes(className) ?? false;
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

type FootnoteSyncContext = {
    listItemKey: string | null;
    refKey: string | null;
    parentListNode: ProseMirrorNode | null;
    parentListPos: number | null;
    parentListChildCount: number;
};

type FootnoteContentNode = {
    node: ProseMirrorNode;
    pos: number;
    key: string | null;
};

type FootnoteListItemNode = FootnoteContentNode & {
    parentListNode: ProseMirrorNode | null;
    parentListPos: number | null;
    parentListChildCount: number;
};

type FootnoteDocumentInfo = {
    refKeys: Set<string>;
    sources: FootnoteContentNode[];
    targets: FootnoteContentNode[];
    listItems: FootnoteListItemNode[];
};

function normalizeFootnoteMarkerText(text: string) {
    return text.trim().replace(/\.$/, "");
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

    if (node.type.name === "orderedList") {
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

function collectFootnoteDocumentInfo(doc: ProseMirrorNode): FootnoteDocumentInfo {
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

function getDeletedFootnoteRefKeys(oldDoc: ProseMirrorNode, newDoc: ProseMirrorNode) {
    const oldRefKeys = collectFootnoteDocumentInfo(oldDoc).refKeys;
    const newRefKeys = collectFootnoteDocumentInfo(newDoc).refKeys;

    return Array.from(oldRefKeys).filter(key => !newRefKeys.has(key));
}

function getFootnoteListItemDeletionRanges(listItems: FootnoteListItemNode[], deletedRefKeys: string[]) {
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

function createFootnoteSyncPlugin() {
    return new Plugin({
        key: new PluginKey("wjFootnoteSync"),
        appendTransaction(transactions, oldState, newState) {
            if (!transactions.some(transaction => transaction.docChanged)) {
                return null;
            }

            const newFootnoteInfo = collectFootnoteDocumentInfo(newState.doc);
            const deletedRefKeys = getDeletedFootnoteRefKeys(oldState.doc, newState.doc);
            const deletionRanges = getFootnoteListItemDeletionRanges(newFootnoteInfo.listItems, deletedRefKeys);

            if (deletionRanges.length > 0) {
                const transaction = newState.tr;

                deletionRanges.forEach(range => {
                    transaction.delete(range.from, range.to);
                });

                return transaction;
            }

            const { sources, targets } = newFootnoteInfo;

            if (sources.length === 0 || targets.length === 0) {
                return null;
            }

            const sourceByKey = new Map<string, FootnoteContentNode>();
            sources.forEach(source => {
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
                    const source = target.key ? sourceByKey.get(target.key) : sources[targetIndex];

                    if (!source || target.node.content.eq(source.node.content)) {
                        return;
                    }

                    transaction.replaceWith(
                        target.pos + 1,
                        target.pos + target.node.nodeSize - 1,
                        source.node.content,
                    );
                    changed = true;
                });

            return changed ? transaction : null;
        },
    });
}

const WJBlockTagExtension = Node.create({
    name: "wjBlockTag",
    priority: 1,
    group: "block",
    content: "block*",
    defining: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !shouldPreserveBlockElement(element)) {
                        return false;
                    }

                    return parsePreservedElement(element);
                },
            },
        ];
    },

    renderHTML: renderPreservedElement,
});

const WJTextBlockTagExtension = Node.create({
    name: "wjTextBlockTag",
    priority: 1,
    group: "block",
    content: "inline*",
    defining: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !shouldPreserveTextBlockElement(element)) {
                        return false;
                    }

                    return parsePreservedElement(element);
                },
            },
        ];
    },

    renderHTML: renderPreservedElement,
});

const WJInlineTagExtension = Node.create({
    name: "wjInlineTag",
    priority: 1,
    group: "inline",
    inline: true,
    content: "inline*",
    defining: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !shouldPreserveInlineElement(element)) {
                        return false;
                    }

                    return parsePreservedElement(element);
                },
            },
        ];
    },

    renderHTML: renderPreservedElement,
});

const WJVoidTagExtension = Node.create({
    name: "wjVoidTag",
    priority: 1,
    group: "inline",
    inline: true,
    atom: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !shouldPreserveVoidElement(element)) {
                        return false;
                    }

                    return parsePreservedElement(element);
                },
            },
        ];
    },

    renderHTML: renderPreservedVoidElement,
});

export const WJTagExtension = Extension.create({
    name: "wjTag",
    priority: 1,

    addGlobalAttributes() {
        return [
            {
                types: nativeAttributeTypes,
                attributes: Object.fromEntries(
                    preservedGlobalAttributes.map(name => [
                        name,
                        {
                            default: null,
                            parseHTML: (element: HTMLElement) =>
                                name === "hidden"
                                    ? (element.hasAttribute("hidden") ? "" : null)
                                    : element.getAttribute(name),
                            renderHTML: (attributes: Record<string, string | null>) =>
                                attributes[name] === null || attributes[name] === undefined
                                    ? {}
                                    : { [name]: attributes[name] },
                        },
                    ]),
                ),
            },
        ];
    },

    addExtensions() {
        return [
            WJBlockTagExtension,
            WJTextBlockTagExtension,
            WJInlineTagExtension,
            WJVoidTagExtension,
        ];
    },

    addProseMirrorPlugins() {
        return [
            createFootnoteSyncPlugin(),
        ];
    },
});
