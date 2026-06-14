// btnDeleteTabView.ts is used to delete whole TabView in the TipTap editor

import { getEditor } from "../../editor/instance.ts";

export function deleteTabView() {
    getEditor()
        ?.chain()
        .focus()
        .command(({ state, tr }) => {
            for (
                let depth = state.selection.$from.depth;
                depth > 0;
                depth -= 1
            ) {
                const node = state.selection.$from.node(depth);

                if (node.type.name !== "tabView") {
                    continue;
                }

                const from = state.selection.$from.before(depth);
                tr.delete(from, from + node.nodeSize);

                return true;
            }

            return false;
        })
        .run();
}
