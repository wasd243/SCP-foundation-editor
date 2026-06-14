import { getEditor } from "../../editor/instance.ts";
import { createTabId } from "./createTabId.ts";

export function addTab() {
    getEditor()
        ?.chain()
        .focus()
        .command(({ state, tr }) => {
            const schema = state.schema;
            const tabViewButton = schema.nodes.tabViewButton;
            const tabViewPanel = schema.nodes.tabViewPanel;
            const paragraph = schema.nodes.paragraph;

            if (!tabViewButton || !tabViewPanel || !paragraph) return false;

            for (
                let depth = state.selection.$from.depth;
                depth > 0;
                depth -= 1
            ) {
                const node = state.selection.$from.node(depth);

                if (node.type.name !== "tabView") {
                    continue;
                }

                const tabViewStart = state.selection.$from.before(depth);
                const buttonList = node.child(0);
                const panelList = node.child(1);
                const tabNumber = buttonList.childCount + 1;
                const buttonId = createTabId();
                const panelId = createTabId();

                const button = tabViewButton.create(
                    {
                        class: "wj-tabs-button",
                        id: buttonId,
                        role: "tab",
                        "aria-label": `Tab ${tabNumber}`,
                        "aria-selected": "false",
                        "aria-controls": panelId,
                        tabindex: "-1",
                    },
                    schema.text(`Tab ${tabNumber}`),
                );

                const panel = tabViewPanel.create(
                    {
                        class: "wj-tabs-panel",
                        id: panelId,
                        role: "tabpanel",
                        "aria-labelledby": buttonId,
                        tabindex: "0",
                        hidden: "",
                    },
                    paragraph.create(),
                );

                const buttonInsertPos =
                    tabViewStart + 1 + buttonList.nodeSize - 1;
                const panelInsertPos =
                    tabViewStart +
                    1 +
                    buttonList.nodeSize +
                    panelList.nodeSize -
                    1;

                tr.insert(panelInsertPos, panel);
                tr.insert(buttonInsertPos, button);

                return true;
            }

            return false;
        })
        .run();
}
