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

export function insertEditorTabView() {
    const editor = getEditor();

    if (!editor) {
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
