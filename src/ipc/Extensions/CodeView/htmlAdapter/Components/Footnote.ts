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

function makeFootnoteListTitleNonEditable({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-title") return null;

  const inFootnoteList = element.closest("wj-footnote-list");
  if (!inFootnoteList) return null;

  element.setAttribute("contenteditable", "false");
  return null;
}

function makeFootnoteListItemContentsEditable({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-footnote-list-item-contents") return null;

  element.setAttribute("contenteditable", "true");
  return null;
}

export const footnoteReplacer: DOMReplacer[] = [
  replaceFootnoteInlineTag,
  makeFootnoteListTitleNonEditable,
  makeFootnoteListItemContentsEditable,
];
