import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceAlign({ element, children }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLDivElement)) return null;

  // List for allowed aligns
  const allowedAligns = ["left", "right", "center"];

  if (!allowedAligns.includes(element.style.textAlign)) {
    return null;
  }

  if (!(children[0] instanceof HTMLElement)) return null;

  const align = element.style.textAlign;
  const child = children[0] as HTMLElement;

  // List for allowed elements
  const allowedElements = ["p", "details"];

  if (!allowedElements.includes(child.tagName.toLowerCase())) return null;

  child.style.textAlign = align;

  if (element.childNodes.length === 1) {
    return child;
  }

  const fragment = document.createDocumentFragment();

  while (element.firstChild) {
    fragment.appendChild(element.firstChild);
  }

  return fragment;
}

export const alignReplacer: DOMReplacer[] = [
  replaceAlign,
];
