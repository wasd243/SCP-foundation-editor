// Collapsible.ts is made for TipTap's collapsible blank lines

import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceCollapsibleContent({ element }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLBRElement)) return null;
  if (element.parentElement?.getAttribute("data-type") !== "detailsContent") return null;

  return document.createElement("p");
}

export const collapsibleReplacer: DOMReplacer[] = [
  replaceCollapsibleContent,
];
