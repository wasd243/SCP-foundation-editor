import { deleteTabView } from "./TabView/btnDeleteTabView.ts";
import { addTab } from "./TabView/btnAddTab.ts";

// Different function name to make a connection with the editor, also prevents name collision
export function addTabInTipTapEditor() {
    addTab();
}

export function deleteTabViewInTipTapEditor() {
    deleteTabView();
}
