import { alignReplacer } from "./Components/Align";
import { codeReplacer } from "./Components/Code";
import { collapsibleReplacer } from "./Components/Collapsible";
import { footnoteReplacer } from "./Components/Footnote";
import { imageBlockReplacer } from "./Components/ImageBlock";
import { tabViewReplacer } from "./Components/TabView";

export type DOMReplaceContext = {
    element: Element;
    children: Element[];
};

export type DOMReplacer = (context: DOMReplaceContext) => Node | null;

const crossoriginAttributeRegex =
    /\s+crossorigin(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]+))?/gi;

const domReplacer: DOMReplacer[] = [
    ...codeReplacer,
    ...imageBlockReplacer,
    ...alignReplacer,
    ...footnoteReplacer,
    // Replace collapsible blocks
    ...collapsibleReplacer,
    ...tabViewReplacer,
];

export function scanDOMandReplace(
    html: string,
    handlers = domReplacer,
): string {
    const template = document.createElement("template");
    template.innerHTML = html.replace(crossoriginAttributeRegex, "");

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
