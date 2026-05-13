import { getEditor } from "../../editor.ts";
import { createTabId } from "../../btnContextMenu/TabView/createTabId.ts";
import tabViewTemplate from "../../json/tabview.json";

function createTabViewContent(buttonId: string, panelId: string) {
    return JSON.parse(
        JSON.stringify(tabViewTemplate)
            .replaceAll("__BUTTON_ID__", buttonId)
            .replaceAll("__PANEL_ID__", panelId),
    );
}

function selectionInsideTabView() {
    const selection = getEditor()?.state.selection;

    if (!selection) {
        return false;
    }

    for (let depth = selection.$from.depth; depth > 0; depth -= 1) {
        if (selection.$from.node(depth).type.name === "tabView") {
            return true;
        }
    }

    // No TabView insertion in another Tabview
    return false;
}

export function insertEditorTabView() {
    const editor = getEditor();

    if (!editor || selectionInsideTabView()) {
        return;
    }

    const idBase = createTabId();
    const buttonId = `${idBase}-button-1`;
    const panelId = `${idBase}-panel-1`;

    editor
        .chain()
        .focus()
        .insertContent(createTabViewContent(buttonId, panelId))
        .run();
}
