import type { JSONContent } from "@tiptap/core";

import { getEditor } from "../../editor.ts";
import { promptInput } from "../../inputWindow.ts";

export function isSupportedImageUrl(url: string) {
    return /^https?:\/\//i.test(url);
}

export function alertUnsupportedImageUrl() {
    window.alert("Only http:// and https:// image URLs are supported.");
}

function createImageContent(src: string): JSONContent {
    return {
        type: "image",
        attrs: {
            src,
            imageAttributes: {
                src,
            },
            wrapperAttributes: {
                class: "image-container",
                contenteditable: "false",
            },
        },
    };
}

export function insertEditorImage(rawUrl: string) {
    const editor = getEditor();
    const src = rawUrl.trim();

    if (!editor || !src) {
        return;
    }

    if (!isSupportedImageUrl(src)) {
        alertUnsupportedImageUrl();
        return;
    }

    editor.chain().focus().insertContent(createImageContent(src)).run();
}

export async function promptEditorImage() {
    const url = await promptInput({
        title: "Insert image",
        label: "Image URL",
        placeholder: "https://…",
        confirmText: "Insert",
    });

    if (url === null) {
        return;
    }

    insertEditorImage(url);
}
