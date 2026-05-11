import { getEditor, type EditorTextAlign } from "../../editor.ts";

export function setEditorAlign(align: EditorTextAlign) {
    getEditor()
        ?.chain()
        .focus()
        .command(({ state, tr }) => {
            const targetTypes = new Set(["details", "detailsSummary", "detailsContent"]);
            const touchedPositions = new Set<number>();

            function updateNode(pos: number) {
                if (touchedPositions.has(pos)) return;

                const node = tr.doc.nodeAt(pos);
                if (!node || !targetTypes.has(node.type.name)) return;

                touchedPositions.add(pos);
                tr.setNodeMarkup(pos, undefined, {
                    ...node.attrs,
                    textAlign: align,
                }, node.marks);
            }

            state.doc.nodesBetween(state.selection.from, state.selection.to, (node, pos) => {
                if (targetTypes.has(node.type.name)) {
                    updateNode(pos);
                }
            });

            for (let depth = state.selection.$from.depth; depth > 0; depth -= 1) {
                const node = state.selection.$from.node(depth);
                if (targetTypes.has(node.type.name)) {
                    updateNode(state.selection.$from.before(depth));
                }
            }

            return true;
        })
        .updateAttributes("paragraph", { textAlign: align })
        .updateAttributes("heading", { textAlign: align })

        // Special case for collapsible blocks
        .updateAttributes("details", { textAlign: align })
        .updateAttributes("detailsSummary", { textAlign: align })
        .updateAttributes("detailsContent", { textAlign: align })
        .run();
}

// Empty function for future Tauri/Rust integration
export function btnAlignIdleInterface() {}
