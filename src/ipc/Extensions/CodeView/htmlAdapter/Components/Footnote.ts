import type { DOMReplaceContext, DOMReplacer } from "../scanDOMandReplace";

const footnoteInlineTags = new Set([
  "wj-footnote-ref-marker",
  "wj-footnote-list-item-marker",
]);

const footnoteKeyAttributes = [
  "data-footnote-id",
  "footnote-id",
  "data-id",
  "id",
  "href",
];

const watchedRoots = new WeakMap<Node, MutationObserver>();
const syncingRoots = new WeakSet<Node>();

function copyAttributes(source: Element, target: HTMLElement) {
  Array.from(source.attributes).forEach(attribute => {
    target.setAttribute(attribute.name, attribute.value);
  });
}

function normalizeFootnoteKey(value: string | null): string | null {
  if (!value) return null;

  const trimmed = value.trim();
  if (!trimmed) return null;

  return trimmed.replace(/^#/, "");
}

function getElementFootnoteKey(element: Element | null): string | null {
  if (!element) return null;

  for (const attr of footnoteKeyAttributes) {
    const key = normalizeFootnoteKey(element.getAttribute(attr));
    if (key) return key;
  }

  return null;
}

function getRootNodeForQueries(element: Element): Document | DocumentFragment | Element | null {
  const root = element.getRootNode();

  if (root instanceof Document || root instanceof DocumentFragment || root instanceof Element) {
    return root;
  }

  return null;
}

function queryAllFromRoot(element: Element, selector: string): Element[] {
  const root = getRootNodeForQueries(element);
  if (!root) return [];

  return Array.from(root.querySelectorAll(selector));
}

function lockClassedElementsInsideFootnoteRef(element: Element) {
  const refs = queryAllFromRoot(element, "wj-footnote-ref");

  refs.forEach(ref => {
    if (ref.hasAttribute("class")) {
      ref.setAttribute("contenteditable", "false");
    }

    ref.querySelectorAll("[class]").forEach(classedElement => {
      classedElement.setAttribute("contenteditable", "false");
    });
  });
}

function getFootnoteListContents(element: Element): Element[] {
  return queryAllFromRoot(element, "li.wj-footnote-list-item wj-footnote-list-item-contents");
}

function syncAllFootnoteRefContents(element: Element) {
  const refs = queryAllFromRoot(element, "wj-footnote-ref-contents");
  if (refs.length === 0) return;

  const listContents = getFootnoteListContents(element);
  if (listContents.length === 0) return;

  refs.forEach(refContents => {
    refContents.setAttribute("contenteditable", "false");

    const refKey =
      getElementFootnoteKey(refContents) ??
      getElementFootnoteKey(refContents.closest("wj-footnote-ref"));

    let source: Element | undefined;

    if (refKey) {
      source = listContents.find(item => {
        const itemKey =
          getElementFootnoteKey(item) ??
          getElementFootnoteKey(item.closest("li.wj-footnote-list-item"));
        return itemKey === refKey;
      });
    }

    if (!source) {
      const index = refs.indexOf(refContents);
      if (index >= 0) {
        source = listContents[index];
      }
    }

    if (!source) return;

    if (refContents.innerHTML !== source.innerHTML) {
      refContents.innerHTML = source.innerHTML;
    }
  });
}

function runFootnoteSync(element: Element) {
  lockClassedElementsInsideFootnoteRef(element);
  syncAllFootnoteRefContents(element);
}

function ensureFootnoteWatchdog(element: Element) {
  const root = getRootNodeForQueries(element);
  if (!root || watchedRoots.has(root)) return;

  const observer = new MutationObserver(() => {
    if (syncingRoots.has(root)) return;

    syncingRoots.add(root);
    try {
      const probe =
        root instanceof Document
          ? root.documentElement
          : root instanceof DocumentFragment
            ? root.firstElementChild
            : root;

      if (probe) {
        runFootnoteSync(probe);
      }
    } finally {
      syncingRoots.delete(root);
    }
  });

  observer.observe(root, {
    subtree: true,
    childList: true,
    characterData: true,
    attributes: true,
  });

  watchedRoots.set(root, observer);
}

function replaceFootnoteInlineTag({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();

  if (!footnoteInlineTags.has(tagName)) return null;

  const span = document.createElement("span");

  copyAttributes(element, span);
  span.setAttribute("contenteditable", "false");

  while (element.firstChild) {
    span.appendChild(element.firstChild);
  }

  return span;
}

function makeFootnoteListTitleNonEditable({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-title") return null;

  const inFootnoteList = element.closest("wj-footnote-list");
  if (!inFootnoteList) return null;

  element.setAttribute("contenteditable", "false");
  return null;
}

function makeFootnoteListItemContentsEditable({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-footnote-list-item-contents") return null;

  const inFootnoteListItem = element.closest("li.wj-footnote-list-item");
  element.setAttribute("contenteditable", inFootnoteListItem ? "true" : "false");
  return null;
}

function syncFootnoteRefContentsAndLock({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();

  if (tagName !== "wj-footnote-ref-contents") return null;

  element.setAttribute("contenteditable", "false");
  runFootnoteSync(element);
  ensureFootnoteWatchdog(element);

  return null;
}

function lockFootnoteRefClassedElements({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-footnote-ref") return null;

  lockClassedElementsInsideFootnoteRef(element);
  ensureFootnoteWatchdog(element);

  return null;
}

function watchFootnoteListItemContents({ element }: DOMReplaceContext): Node | null {
  const tagName = element.tagName.toLowerCase();
  if (tagName !== "wj-footnote-list-item-contents") return null;

  ensureFootnoteWatchdog(element);
  runFootnoteSync(element);

  return null;
}

export const footnoteReplacer: DOMReplacer[] = [
  replaceFootnoteInlineTag,
  makeFootnoteListTitleNonEditable,
  makeFootnoteListItemContentsEditable,
  lockFootnoteRefClassedElements,
  syncFootnoteRefContentsAndLock,
  watchFootnoteListItemContents,
];
