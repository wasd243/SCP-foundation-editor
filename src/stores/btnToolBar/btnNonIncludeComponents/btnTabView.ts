import { getEditor } from "../../editor.ts";
import { createTabId } from "../../btnContextMenu/TabView/createTabId.ts";

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
        .insertContent({
            type: "tabView",
            content: [
                {
                    type: "tabViewButtonList",
                    attrs: {
                        class: "wj-tabs-button-list",
                        role: "tablist",
                    },
                    content: [
                        {
                            type: "tabViewButton",
                            attrs: {
                                class: "wj-tabs-button",
                                id: buttonId,
                                role: "tab",
                                "aria-label": "Tab 1",
                                "aria-selected": "true",
                                "aria-controls": panelId,
                                tabindex: "0",
                            },
                            content: [
                                {
                                    type: "text",
                                    text: "Tab 1",
                                },
                            ],
                        },
                    ],
                },
                {
                    type: "tabViewPanelList",
                    attrs: {
                        class: "wj-tabs-panel-list",
                    },
                    content: [
                        {
                            type: "tabViewPanel",
                            attrs: {
                                class: "wj-tabs-panel",
                                id: panelId,
                                role: "tabpanel",
                                "aria-labelledby": buttonId,
                                tabindex: "0",
                                hidden: null,
                            },
                            content: [
                                {
                                    type: "paragraph",
                                },
                            ],
                        },
                    ],
                },
            ],
        })
        .run();
}
