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

function setCodeBlockLanguageAttributes(element: HTMLElement, language: string | null) {
    Array.from(element.classList)
        .filter(className => className.startsWith("wj-language-"))
        .forEach(className => element.classList.remove(className));

    element.classList.add("wj-code");

    if (language) {
        element.classList.add(`wj-language-${language}`);
        element.dataset.language = language;
    } else {
        delete element.dataset.language;
    }
}

function setCodeLanguageAttributes(element: HTMLElement, language: string | null) {
    element.className = "";

    if (language) {
        element.classList.add(`${languageClassPrefix}${language}`);
    }
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

    addNodeView() {
        return ({ node, getPos, editor, HTMLAttributes }) => {
            let currentNode = node;
            const dom = document.createElement("div");
            const panel = document.createElement("div");
            const languageInput = document.createElement("input");
            const contentDOM = document.createElement("code");

            dom.classList.add("wj-code");
            panel.classList.add("wj-code-panel");
            languageInput.classList.add("wj-code-language-input");
            languageInput.type = "text";
            languageInput.placeholder = "code";
            languageInput.title = "Code language";
            languageInput.spellcheck = false;
            languageInput.autocapitalize = "off";
            languageInput.autocomplete = "off";
            languageInput.setAttribute("aria-label", "Code language");
            panel.contentEditable = "false";

            dom.appendChild(panel);
            panel.appendChild(languageInput);
            dom.appendChild(contentDOM);

            function updateLanguage(nextLanguage: string | null) {
                setCodeBlockLanguageAttributes(dom, nextLanguage);
                setCodeLanguageAttributes(contentDOM, nextLanguage);
                languageInput.value = nextLanguage ?? "";
            }

            function getNodePosition() {
                return typeof getPos === "function" ? getPos() : null;
            }

            Object.entries(HTMLAttributes).forEach(([name, value]) => {
                if (typeof value === "string") {
                    dom.setAttribute(name, value);
                }
            });

            updateLanguage(normalizeLanguage(node.attrs.language));

            languageInput.addEventListener("input", () => {
                const position = getNodePosition();
                const language = normalizeLanguage(languageInput.value);

                if (position === null) return;

                editor.view.dispatch(
                    editor.view.state.tr.setNodeMarkup(position, undefined, {
                        ...currentNode.attrs,
                        language,
                    }),
                );
            });

            return {
                dom,
                contentDOM,
                update: updatedNode => {
                    if (updatedNode.type !== currentNode.type) return false;

                    currentNode = updatedNode;
                    updateLanguage(normalizeLanguage(updatedNode.attrs.language));
                    return true;
                },
            };
        };
    },
}).configure({
    lowlight,
    languageClassPrefix,
    HTMLAttributes: {
        class: "wj-code",
    },
});
