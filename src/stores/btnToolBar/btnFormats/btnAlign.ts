import { getEditor, type EditorTextAlign } from "../../editor.ts";

function setTextAlignStyle(style: unknown, align: EditorTextAlign) {
    const declarations = typeof style === "string"
        ? style
            .split(";")
            .map(declaration => declaration.trim())
            .filter(declaration => declaration && !/^text-align\s*:/i.test(declaration))
        : [];

    declarations.push(`text-align: ${align}`);

    return `${declarations.join("; ")};`;
}

export function setEditorAlign(align: EditorTextAlign) {
    getEditor()
        ?.chain()
        .focus()
        .command(({ state, tr }) => {
            const targetTypes = new Set(["paragraph", "heading", "detailsSummary"]);
            const touchedPositions = new Set<number>();

            function updateNode(pos: number) {
                if (touchedPositions.has(pos)) return;

                const node = tr.doc.nodeAt(pos);
                if (!node || !targetTypes.has(node.type.name)) return;

                touchedPositions.add(pos);
                tr.setNodeMarkup(pos, undefined, {
                    ...node.attrs,
                    textAlign: align,
                    style: setTextAlignStyle(node.attrs.style, align),
                }, node.marks);
            }

            if (state.selection.empty) {
                for (let depth = state.selection.$from.depth; depth > 0; depth -= 1) {
                    const node = state.selection.$from.node(depth);

                    if (targetTypes.has(node.type.name)) {
                        updateNode(state.selection.$from.before(depth));
                        break;
                    }
                }
            } else {
                state.doc.nodesBetween(state.selection.from, state.selection.to, (node, pos) => {
                    if (targetTypes.has(node.type.name)) {
                        updateNode(pos);
                    }
                });
            }

            return true;
        })
        .run();
}

// Empty function for future Tauri/Rust integration
export function btnAlignIdleInterface() {}
