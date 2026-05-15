import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const footnoteInlineTags = new Set([
  "wj-footnote-ref-marker",
  "wj-footnote-list-item-marker",
]);

const footnoteKeyAttributes = [
  "data-footnote-id",
  "footnote-id",
  "data-id",
  "id",
  "href",
];

function copyAttributes(source: Element, target: HTMLElement) {
  Array.from(source.attributes).forEach(attribute => {
    target.setAttribute(attribute.name, attribute.value);
  });
}

function normalizeFootnoteKey(value: string | null): string | null {
  if (!value) return null;

  const trimmed = value.trim();
  if (!trimmed) return null;

  return trimmed.replace(/^#/, "");
}

function getElementFootnoteKey(element: Element | null): string | null {
  if (!element) return null;

  for (const attr of footnoteKeyAttributes) {
    const key = normalizeFootnoteKey(element.getAttribute(attr));
    if (key) return key;
  }

  return null;
}

function queryAllFromRoot(element: Element, selector: string): Element[] {
  const root = element.getRootNode();

  if (root instanceof Document || root instanceof DocumentFragment) {
    return Array.from(root.querySelectorAll(selector));
  }

  if (root instanceof Element) {
    return Array.from(root.querySelectorAll(selector));
  }

  return [];
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

function syncFootnoteRefContentsAndLock({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-footnote-ref-contents") return null;

  element.setAttribute("contenteditable", "false");

  const listContents = queryAllFromRoot(element, "wj-footnote-list-item-contents");
  if (listContents.length === 0) return null;

  const refKey =
    getElementFootnoteKey(element) ??
    getElementFootnoteKey(element.closest("wj-footnote-ref"));

  let source: Element | undefined;

  if (refKey) {
    source = listContents.find(item => {
      const itemKey =
        getElementFootnoteKey(item) ??
        getElementFootnoteKey(item.closest("wj-footnote-list-item"));
      return itemKey === refKey;
    });
  }

  if (!source) {
    const refContents = queryAllFromRoot(element, "wj-footnote-ref-contents");
    const index = refContents.indexOf(element);
    if (index >= 0) {
      source = listContents[index];
    }
  }

  if (!source) return null;

  if (element.innerHTML !== source.innerHTML) {
    element.innerHTML = source.innerHTML;
  }

  return null;
}

export const footnoteReplacer: DOMReplacer[] = [
  replaceFootnoteInlineTag,
  makeFootnoteListTitleNonEditable,
  makeFootnoteListItemContentsEditable,
  syncFootnoteRefContentsAndLock,
];
