import * as csstree from "css-tree";

export function addImportant(ast: csstree.CssNode): void {
    csstree.walk(ast, {
        visit: "Declaration",
        enter(node) {
            if (!node.property.startsWith("--")) {
                node.important = true;
            }
        },
    });
}
