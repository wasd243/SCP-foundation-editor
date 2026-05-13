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
  if (!footnoteInlineTags.has(element.tagName.toLowerCase())) return null;

  const span = document.createElement("span");

  copyAttributes(element, span);

  while (element.firstChild) {
    span.appendChild(element.firstChild);
  }

  return span;
}

export const footnoteReplacer: DOMReplacer[] = [
  replaceFootnoteInlineTag,
];
