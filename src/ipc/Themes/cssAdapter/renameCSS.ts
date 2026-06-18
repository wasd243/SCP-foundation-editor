import * as csstree from "css-tree";

// Full-selector replacements — matched against the whole selector string.
// Must be checked before simple class renames to avoid partial renames
// corrupting compound patterns (e.g. .yui-nav must not become .wj-tabs-button-list
// before .yui-nav li is matched).
const COMPOUND_RENAME_MAP: Record<string, string> = {
    ".yui-nav li a em": ".wj-tabs-button-label",
    ".yui-nav li.selected": '.wj-tabs-button[aria-selected="true"]',
    ".yui-nav li a": ".wj-tabs-button",
    ".yui-nav li": ".wj-tabs-button",
};

// Single class-token renames applied after compound renames.
const RENAME_MAP: Record<string, string> = {
    "page-rate-widget-box": "rateBox",
    "yui-navset": "wj-tabs",
    "yui-nav": "wj-tabs-button-list",
    "yui-content": "wj-tabs-panel-list",
    "scp-image-block": "image-container",
    "image-block": "image-container",
    ".code": ".wj-code",
    "footnotes-footer": "wj-footnote-list",
    "wiki-note": "wj-note",
};

// ID → class renames (node type changes from IdSelector to ClassSelector)
const ID_TO_CLASS_MAP: Record<string, string> = {
    "page-content": "ProseMirror",
};

function normalizeSelector(s: string): string {
    return s.replace(/\s+/g, " ").trim();
}

export function renameCSS(ast: csstree.CssNode): void {
    // Pass 1: replace full selectors that match a compound pattern
    csstree.walk(ast, {
        visit: "SelectorList",
        enter(node) {
            node.children.forEach((selector, selectorItem) => {
                const text = normalizeSelector(csstree.generate(selector));
                const target = COMPOUND_RENAME_MAP[text];
                if (target !== undefined) {
                    selectorItem.data = csstree.parse(target, {
                        context: "selector",
                    }) as csstree.CssNode;
                }
            });
        },
    });

    // Pass 1.5: replace ID selectors that map to a class
    csstree.walk(ast, {
        visit: "IdSelector",
        enter(node) {
            const renamed = ID_TO_CLASS_MAP[node.name];
            if (renamed !== undefined) {
                // mutate the node in place: change type id → class
                (node as any).type = "ClassSelector";
                node.name = renamed;
            }
        },
    });

    // Pass 2: rename individual class tokens not already handled above
    csstree.walk(ast, {
        visit: "ClassSelector",
        enter(node) {
            const renamed = RENAME_MAP[node.name];
            if (renamed !== undefined) {
                node.name = renamed;
            }
        },
    });
    // debug output for testing
    // console.log(ast);
}
