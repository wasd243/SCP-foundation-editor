import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const WJ_LANGUAGE_CLASS_PREFIX = "wj-language-";
const TIPTAP_LANGUAGE_CLASS_PREFIX = "language-";

function normalizeLanguage(language: string | null | undefined) {
  const normalized = language?.trim().toLowerCase();

  return normalized || null;
}

function getLanguageFromClassList(element: Element, prefix: string) {
  const languageClass = Array.from(element.classList).find(className =>
    className.startsWith(prefix),
  );

  return normalizeLanguage(languageClass?.slice(prefix.length));
}

function getCodeLanguage(element: Element, codeElement: HTMLElement | null) {
  return (
    getLanguageFromClassList(element, WJ_LANGUAGE_CLASS_PREFIX) ??
    normalizeLanguage(element.querySelector(".wj-code-language")?.textContent) ??
    (codeElement ? getLanguageFromClassList(codeElement, TIPTAP_LANGUAGE_CLASS_PREFIX) : null)
  );
}

function replaceWJCodeBlock({ element }: DOMReplaceContext): Node | null {
  if (element.tagName.toLowerCase() !== "wj-code") return null;

  const codeElement = element.querySelector("pre > code, code");
  if (!(codeElement instanceof HTMLElement)) return null;

  const language = getCodeLanguage(element, codeElement);
  const pre = document.createElement("pre");
  const code = document.createElement("code");

  pre.classList.add("wj-code");

  if (language) {
    pre.classList.add(`${WJ_LANGUAGE_CLASS_PREFIX}${language}`);
    pre.dataset.language = language;
    code.classList.add(`${TIPTAP_LANGUAGE_CLASS_PREFIX}${language}`);
  }

  code.textContent = codeElement.textContent;
  pre.appendChild(code);

  return pre;
}

export const codeReplacer: DOMReplacer[] = [
  replaceWJCodeBlock,
];
