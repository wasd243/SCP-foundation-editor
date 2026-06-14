import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const footnoteInlineTags = new Set([
    "wj-footnote-ref-marker",
    "wj-footnote-list-item-marker",
]);

// let ALL contents under wj-footnote-list contenteditable = false
function underFootnoteListContentEditableFalse({
    element,
}: DOMReplaceContext): Node | null {
    if (element.tagName !== "P") {
        return null;
    }

    const previous = element.previousElementSibling;

    if (previous && previous.classList.contains("wj-footnote-list")) {
        element.setAttribute("contenteditable", "false");
    }

    return null;
}

function copyAttributes(source: Element, target: HTMLElement) {
    Array.from(source.attributes).forEach((attribute) => {
        target.setAttribute(attribute.name, attribute.value);
    });
}

function hasClass(element: Element, className: string) {
    return element.classList.contains(className);
}

function replaceFootnoteInlineTag({ element }: DOMReplaceContext): Node | null {
    const tagName = element.tagName.toLowerCase();

    if (!footnoteInlineTags.has(tagName)) return null;

    const span = document.createElement("span");

    copyAttributes(element, span);
    span.setAttribute("contenteditable", "false");

    while (element.firstChild) {
        span.appendChild(element.firstChild);
    }

    return span;
}

function makeFootnoteRefReadOnly({ element }: DOMReplaceContext): Node | null {
    if (!hasClass(element, "wj-footnote-ref")) return null;

    element.setAttribute("contenteditable", "false");
    return null;
}

function makeFootnoteRefChromeReadOnly({
    element,
}: DOMReplaceContext): Node | null {
    if (!element.closest(".wj-footnote-ref")) return null;
    if (
        !Array.from(element.classList).some((className) =>
            className.startsWith("wj-footnote-ref"),
        )
    )
        return null;

    element.setAttribute("contenteditable", "false");
    return null;
}

export const footnoteReplacer: DOMReplacer[] = [
    replaceFootnoteInlineTag,
    makeFootnoteRefReadOnly,
    makeFootnoteRefChromeReadOnly,
    underFootnoteListContentEditableFalse,
];
