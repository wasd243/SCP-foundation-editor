import { alignReplacer } from "./Components/Align";
import { collapsibleReplacer } from "./Components/Collapsible";

export type DOMReplaceContext = {
  element: Element;
  children: Element[];
};

export type DOMReplacer = (context: DOMReplaceContext) => Node | null;

const domReplacer: DOMReplacer[] = [
  ...alignReplacer,
  // Replace collapsible content for TipTap empty line
  ...collapsibleReplacer,
];

export function scanDOMandReplace(html: string, handlers = domReplacer): string {
  const template = document.createElement("template");
  template.innerHTML = html;

  template.content.querySelectorAll("*").forEach((element) => {
    const context = {
      element,
      children: Array.from(element.children),
    };

    for (const handler of handlers) {
      if (!element.parentNode) break;

      const replacement = handler(context);
      if (!replacement) continue;

      element.replaceWith(replacement);
      break;
    }
  });

  return template.innerHTML;
}
