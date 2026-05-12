// Collapsible.ts is made for TipTap's collapsible blank lines

import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceCollapsibleContent({ element }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLBRElement)) return null;
  if (element.parentElement?.getAttribute("data-type") !== "detailsContent") return null;

  return document.createElement("p");
}

function adaptCollapsibleSummaryText({ element }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLDetailsElement)) return null;

  const summary = element.querySelector(":scope > summary");
  if (!summary) return null;

  const showText = element.querySelector(":scope > .wj-collapsible-show-text");
  const hideText = element.querySelector(":scope > .wj-collapsible-hide-text");
  if (!showText && !hideText) return null;

  if (showText) {
    summary.append(showText);
  }

  if (hideText) {
    summary.append(hideText);
  }

  return element;
}

export const collapsibleReplacer: DOMReplacer[] = [
  adaptCollapsibleSummaryText,
  replaceCollapsibleContent,
];
