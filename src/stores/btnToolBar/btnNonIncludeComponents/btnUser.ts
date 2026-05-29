import { getEditor } from "../../editor.ts";

const defaultUserText = "User";

type UserClassName = "wj-user" | "wj-user-with-img";

function insertEditorUserNode(className: UserClassName) {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const position = editor.state.selection.from;

    editor
        .chain()
        .focus()
        .insertContent(`<span class="${className}">${defaultUserText}</span>`)
        .run();

    editor.commands.setNodeSelection(position);
}

export function insertEditorUser() {
    insertEditorUserNode("wj-user");
}

export function insertEditorUserWithImg() {
    insertEditorUserNode("wj-user-with-img");
}

export function promptInsertEditorUser() {
    if (window.confirm("Insert [[*user ]]?")) {
        insertEditorUserWithImg();
        return;
    }

    insertEditorUser();
}
