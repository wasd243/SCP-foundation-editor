import { mergeAttributes } from "@tiptap/core";
import { CodeBlockLowlight } from "@tiptap/extension-code-block-lowlight";
import { common, createLowlight } from "lowlight";

const lowlight = createLowlight(common);
const languageClassPrefix = "language-";

function normalizeLanguage(language: unknown) {
    return typeof language === "string" && language.trim()
        ? language.trim().toLowerCase()
        : null;
}

function getLanguageFromClassList(element: Element, prefix: string) {
    const languageClass = Array.from(element.classList).find(className =>
        className.startsWith(prefix),
    );

    return normalizeLanguage(languageClass?.slice(prefix.length));
}

export const CodeBlockLowlightExtension = CodeBlockLowlight.extend({
    addAttributes() {
        return {
            language: {
                default: this.options.defaultLanguage,
                parseHTML: element => {
                    const codeElement = element.firstElementChild;

                    return (
                        normalizeLanguage(element.getAttribute("data-language")) ??
                        (codeElement ? getLanguageFromClassList(codeElement, languageClassPrefix) : null)
                    );
                },
                rendered: false,
            },
        };
    },

    renderHTML({ node, HTMLAttributes }) {
        const language = normalizeLanguage(node.attrs.language);
        const codeAttributes = language
            ? { class: `${languageClassPrefix}${language}` }
            : {};
        const blockAttributes = language
            ? {
                class: `wj-code wj-language-${language}`,
                "data-language": language,
            }
            : {
                class: "wj-code",
            };

        return [
            "pre",
            mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, blockAttributes),
            ["code", codeAttributes, 0],
        ];
    },
}).configure({
    lowlight,
    languageClassPrefix,
    HTMLAttributes: {
        class: "wj-code",
    },
});
