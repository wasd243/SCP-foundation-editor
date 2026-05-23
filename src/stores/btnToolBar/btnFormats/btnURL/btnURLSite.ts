import { promptEditorLink } from "../btnURL.ts";

export function insertURLSiteEditor() {
    promptEditorLink({
        class: "active",
        normalize: false,
        leadingSlash: true,
        promptLabel: "Enter Page Name",
    });
}
