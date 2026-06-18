import * as csstree from "css-tree";

const RENAME_MAP: Record<string, string> = {
    "page-rate-widget-box": "rateBox",
    "scp-image-block": "image-container",
    "image-block": "image-container",
    "code": "wj-code",
    "footnotes-footer": "wj-footnote-list",
    "wiki-note": "wj-note",
};

export function renameCSS(ast: csstree.CssNode): void {
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
