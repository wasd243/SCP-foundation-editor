import * as csstree from "css-tree";

export function renameCSS(ast: csstree.CssNode): void {
    csstree.walk(ast, {
        visit: "ClassSelector",
        enter(node) {
            if (node.name === "page-rate-widget-box") {
                node.name = "rateBox";
            }
        },
    });
    // debug output for testing
    // console.log(ast);
}
