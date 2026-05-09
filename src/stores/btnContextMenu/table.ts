import { getEditor } from "../editor.ts";

export function addTableColumn() {
    getEditor()?.chain().focus().addColumnAfter().run();
}

export function addTableRow() {
    getEditor()?.chain().focus().addRowAfter().run();
}

export function deleteTableColumn() {
    getEditor()?.chain().focus().deleteColumn().run();
}

export function deleteTableRow() {
    getEditor()?.chain().focus().deleteRow().run();
}

export function deleteTable() {
    getEditor()?.chain().focus().deleteTable().run();
}
