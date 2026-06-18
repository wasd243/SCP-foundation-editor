import * as csstree from "css-tree";

const KEEP_ENTRIES = [
    // IDs
    "#container-wrap",
    "#header",
    "#top-bar",
    "#content-wrap",
    "#side-bar",
    "#main-content",
    "#page-content",
    "#page-title", // removed `footer` and `breadcrumb` because the editor doesn't have them
    // Classes
    ".meta-title",
    ".page-rate-widget-box",
    ".code",
    ".scp-image-block",
    ".image-block",
    ".footnotes-footer",
    ".yui-navset",
    // ".Parallel-ACS", // These components cannot support WYSIWYG or really hard which will cause unknown errors, removed.
    // ".Parallel-AIM", // These components cannot support WYSIWYG or really hard which will cause unknown errors, removed.
    ".bblock",
    ".dblock",
    ".keycap",
    ".ruby",
    ".rt",
    ".hovertip",
    // ".printuser", // Remove this because wikidot user img and name cannot get by request/reqwest libraries, might return 418/402/403 if you don't log in to Pro account.
    // ".licensebox", // Remove this because the community already has one license box generator.
    // ".content-panel", // Remove this because I don't know where it should be used in WYSIWYG editor.
    ".table",
    ".scroll-x",
    // Elements
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "p",
    "li",
    "ul",
    "ol",
    "blockquote",
    "div.blockquote",
    "hr",
    "table",
    "th",
    "td",
    "code",
    "pre",
    "tt",
    "sub",
    "sup",
    "b",
    "strong",
    "em",
    "small",
    // Pseudo
    ":root",
    "::selection",
    "::-webkit-scrollbar",
];

const KEEP_WILDCARD_PREFIXES = [
    ".bg-",
    ".b-",
    ".round-",
    ".shadow-",
    ".t-",
    ".w-",
];

const ALLOWED_AT_RULES = new Set(["media", "keyframes", "supports"]);

const BOUNDARY = /^[.:\[(]/;

function leadingToken(selector: string): string {
    const m = selector.match(/^[^\s>~+]+/);
    return m ? m[0] : selector;
}

function matchesKeepList(selector: string): boolean {
    const token = leadingToken(selector.trim());
    for (const prefix of KEEP_WILDCARD_PREFIXES) {
        if (token.startsWith(prefix)) return true;
    }
    for (const entry of KEEP_ENTRIES) {
        if (token === entry) return true;
        if (token.startsWith(entry) && BOUNDARY.test(token[entry.length]))
            return true;
    }
    return false;
}

export function getNecessaryCSS(ast: csstree.CssNode): void {
    console.log("[cssAdapter] getNecessaryCSS: Activated");

    // Step 1: Remove disallowed at-rules (e.g. @font-face, @import)
    csstree.walk(ast, {
        visit: "Atrule",
        enter(node, item, list) {
            if (!ALLOWED_AT_RULES.has(node.name.toLowerCase())) {
                list?.remove(item!);
            }
        },
    });

    // Step 2: Filter rules — remove all-unset rules and non-keep-list rules
    csstree.walk(ast, {
        visit: "Rule",
        enter: function (node, item, list) {
            if (this.atrule?.name.toLowerCase().includes("keyframes")) return;

            // All-unset check
            if (!node.block.children.isEmpty) {
                let allUnset = true;
                node.block.children.forEach((child) => {
                    if (child.type !== "Declaration") {
                        allUnset = false;
                        return;
                    }
                    const decl = child as csstree.Declaration;
                    if (csstree.generate(decl.value).trim() !== "unset")
                        allUnset = false;
                });
                if (allUnset) {
                    list?.remove(item!);
                    return;
                }
            }

            // Allowlist filter — strip non-matching selectors, remove rule if none left
            if (node.prelude.type !== "SelectorList") return;
            const selectorList = node.prelude as csstree.SelectorList;
            const toRemove: csstree.ListItem<csstree.CssNode>[] = [];
            selectorList.children.forEach((selector, selectorItem) => {
                if (!matchesKeepList(csstree.generate(selector)))
                    toRemove.push(selectorItem);
            });
            for (const si of toRemove) selectorList.children.remove(si);
            if (selectorList.children.isEmpty) {
                list?.remove(item!);
            }
        },
    });

    // Step 3: Remove at-rules left empty after rule filtering
    csstree.walk(ast, {
        visit: "Atrule",
        leave(node, item, list) {
            if (node.block && node.block.children.isEmpty) {
                list?.remove(item!);
            }
        },
    });
}
