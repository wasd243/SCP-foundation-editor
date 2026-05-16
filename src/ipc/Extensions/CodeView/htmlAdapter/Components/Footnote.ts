import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const footnoteInlineTags = new Set([
  "wj-footnote-ref-marker",
  "wj-footnote-list-item-marker",
]);

function copyAttributes(source: Element, target: HTMLElement) {
  Array.from(source.attributes).forEach(attribute => {
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

function makeFootnoteRefChromeReadOnly({ element }: DOMReplaceContext): Node | null {
  if (!element.closest(".wj-footnote-ref")) return null;
  if (!Array.from(element.classList).some(className => className.startsWith("wj-footnote-ref"))) return null;

  element.setAttribute("contenteditable", "false");
  return null;
}

function makeFootnoteListTitleReadOnly({ element }: DOMReplaceContext): Node | null {
  if (!hasClass(element, "wj-title")) return null;
  if (!element.closest(".wj-footnote-list")) return null;

  element.setAttribute("contenteditable", "false");
  return null;
}

function makeFootnoteListSeparatorReadOnly({ element }: DOMReplaceContext): Node | null {
  if (!hasClass(element, "wj-footnote-sep")) return null;
  if (!element.closest(".wj-footnote-list-item")) return null;

  element.setAttribute("contenteditable", "false");
  return null;
}

function makeFootnoteListItemContentsEditable({ element }: DOMReplaceContext): Node | null {
  if (!hasClass(element, "wj-footnote-list-item-contents")) return null;

  const inFootnoteListItem = element.closest("li.wj-footnote-list-item");

  if (inFootnoteListItem) {
    element.removeAttribute("contenteditable");
  } else {
    element.setAttribute("contenteditable", "false");
  }

  return null;
}

export const footnoteReplacer: DOMReplacer[] = [
  replaceFootnoteInlineTag,
  makeFootnoteRefReadOnly,
  makeFootnoteRefChromeReadOnly,
  makeFootnoteListTitleReadOnly,
  makeFootnoteListSeparatorReadOnly,
  makeFootnoteListItemContentsEditable,
];
