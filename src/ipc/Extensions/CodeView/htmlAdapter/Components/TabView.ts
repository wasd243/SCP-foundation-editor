import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

function replaceTabViewPanelBreak({ element }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLBRElement)) return null;
  if (!element.parentElement?.classList.contains("wj-tabs-panel")) return null;

  return document.createElement("p");
}

export const tabViewReplacer: DOMReplacer[] = [
  replaceTabViewPanelBreak,
];
