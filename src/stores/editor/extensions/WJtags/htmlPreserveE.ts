import { Node } from "@tiptap/core";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";

export type HTMLAttributes = Record<string, string>;

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
    "li",
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

export const preservedGlobalAttributes = [
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

export const nativeAttributeTypes = [
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

function hasElementClass(element: HTMLElement, className: string) {
    return element.classList.contains(className);
}

function isFootnoteListOrderedElement(element: HTMLElement) {
    return element.tagName.toLowerCase() === "ol" && Boolean(element.closest(".wj-footnote-list"));
}

function isFootnoteListItemElement(element: HTMLElement) {
    return element.tagName.toLowerCase() === "li" && hasElementClass(element, "wj-footnote-list-item");
}

function shouldPreserveNativeElement(element: HTMLElement) {
    return isFootnoteListOrderedElement(element) || isFootnoteListItemElement(element);
}

function isNativeTipTapElement(element: HTMLElement) {
    if (shouldPreserveNativeElement(element)) return false;

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

export function getNodeHTMLAttributes(node: ProseMirrorNode): Record<string, unknown> {
    const htmlAttributes = node.attrs.htmlAttributes;

    if (htmlAttributes && typeof htmlAttributes === "object") {
        return htmlAttributes as Record<string, unknown>;
    }

    return node.attrs;
}

export function getNodeAttribute(node: ProseMirrorNode, name: string): string | null {
    const attributes = getNodeHTMLAttributes(node);
    const value = attributes[name];

    return typeof value === "string" ? value : null;
}

export function getNodeTagName(node: ProseMirrorNode): string | null {
    const tagName = node.attrs.tagName;

    return typeof tagName === "string" ? tagName : null;
}

export function getNodeClassAttribute(node: ProseMirrorNode) {
    return getNodeAttribute(node, "class") ?? "";
}

export function nodeHasClass(node: ProseMirrorNode, className: string) {
    const classAttribute = getNodeClassAttribute(node);

    return classAttribute.split(/\s+/).includes(className);
}

export function removeHTMLAttribute(node: ProseMirrorNode, attributeName: string) {
    const attributes = getNodeHTMLAttributes(node);
    const htmlAttributes = { ...attributes };

    delete htmlAttributes[attributeName];

    if (node.attrs.htmlAttributes && typeof node.attrs.htmlAttributes === "object") {
        return {
            ...node.attrs,
            htmlAttributes,
        };
    }

    return htmlAttributes;
}

const WJBlockTagExtension = Node.create({
    name: "wjBlockTag",
    priority: 1000,
    group: "block",
    content: "block*",
    defining: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1000,
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
    priority: 1000,
    group: "block",
    content: "inline*",
    defining: true,

    addAttributes: createAttributes,

    parseHTML() {
        return [
            {
                tag: "*",
                priority: 1000,
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

export const WJHtmlPreserveExtensions = [
    WJBlockTagExtension,
    WJTextBlockTagExtension,
    WJInlineTagExtension,
    WJVoidTagExtension,
];
