import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceAlign({ element, children }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLDivElement)) return null;

  // List for allowed aligns
  // Temporary remove `justify` option until wj releases it
  const allowedAligns = ["left", "right", "center"];

  if (!allowedAligns.includes(element.style.textAlign)) {
    return null;
  }

  // Only allow <p> as child
  if (children[0].tagName.toLowerCase() !== "p") return null;

  const align = element.style.textAlign;

  const paragraph = children[0] as HTMLParagraphElement;
  paragraph.style.textAlign = align;

  return paragraph;
}

export const alignReplacer: DOMReplacer[] = [
  replaceAlign,
];
