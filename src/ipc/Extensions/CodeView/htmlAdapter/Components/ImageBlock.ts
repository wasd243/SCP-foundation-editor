import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const alignmentClassMap = new Map([
  ["block-left", "alignleft"],
  ["block-right", "alignright"],
  ["block-center", "aligncenter"],
]);

function replaceImageBlock({ element }: DOMReplaceContext): Node | null {
  if (!(element instanceof HTMLDivElement)) return null;
  if (!element.classList.contains("scp-image-block")) return null;

  const alignmentEntry = Array.from(alignmentClassMap.entries())
    .find(([blockClass]) => element.classList.contains(blockClass));

  if (!alignmentEntry) return null;

  const [, alignClass] = alignmentEntry;

  // Future adapters may need to convert block-left/right/center outside scp-image-block.
  element.className = `image-container ${alignClass}`;
  element.setAttribute("contenteditable", "false");
  element.setAttribute("draggable", "true");
  element.querySelectorAll(".scp-image-caption").forEach(caption => {
    caption.setAttribute("contenteditable", "true");
  });

  return element;
}

export const imageBlockReplacer: DOMReplacer[] = [
  replaceImageBlock,
];
