import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceAlign({ element, children }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLDivElement)) return null;

  // List for allowed aligning
  const allowedAligns = ["left", "right", "center"];

  if (!allowedAligns.includes(element.style.textAlign)) {
    return null;
  }

  const align = element.style.textAlign;
  let aligned = false;

  children.forEach(child => {
    if (!(child instanceof HTMLElement)) return;

    const tagName = child.tagName.toLowerCase();

    if (tagName === "p") {
      child.style.textAlign = align;
      aligned = true;
      return;
    }

    if (tagName === "details") {
      const summary = child.querySelector("summary.wj-collapsible-button");

      if (summary instanceof HTMLElement) {
        summary.style.textAlign = align;
        aligned = true;
      }
    }
  });

  if (!aligned) return null;

  if (element.childNodes.length === 1) {
    return element.firstChild;
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
