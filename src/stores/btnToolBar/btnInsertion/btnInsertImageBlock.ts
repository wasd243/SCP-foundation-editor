import type { JSONContent } from "@tiptap/core";

import { getEditor } from "../../editor.ts";
import { promptInput } from "../../inputWindow.ts";
import {
    alertUnsupportedImageUrl,
    isSupportedImageUrl,
} from "./btnInsertImage.ts";

const defaultImageBlockWidth = "200px";
const defaultImageBlockCaption = "CAPTION";

function createImageBlockContent(src: string): JSONContent {
    return {
        type: "wjBlockTag",
        attrs: {
            tagName: "div",
            htmlAttributes: {
                class: "image-container alignright",
                style: `width: ${defaultImageBlockWidth}`,
                "data-editor-export": "include",
                "data-editor-include": "component:image-block",
                contenteditable: "false",
                draggable: "true",
            },
        },
        content: [
            {
                type: "image",
                attrs: {
                    src,
                    imageAttributes: {
                        src,
                    },
                    wrapperAttributes: null,
                },
            },
            {
                type: "wjBlockTag",
                attrs: {
                    tagName: "div",
                    htmlAttributes: {
                        class: "scp-image-caption alignright",
                        contenteditable: "true",
                        "data-editor-export": "div",
                    },
                },
                content: [
                    {
                        type: "paragraph",
                        content: [
                            {
                                type: "text",
                                text: defaultImageBlockCaption,
                            },
                        ],
                    },
                ],
            },
        ],
    };
}

export function insertEditorImageBlock(rawUrl: string) {
    const editor = getEditor();
    const src = rawUrl.trim();

    if (!editor || !src) {
        return;
    }

    if (!isSupportedImageUrl(src)) {
        alertUnsupportedImageUrl();
        return;
    }

    editor.chain().focus().insertContent(createImageBlockContent(src)).run();
}

export async function promptEditorImageBlock() {
    const url = await promptInput({
        title: "Insert image block",
        label: "Image URL",
        placeholder: "https://…",
        confirmText: "Insert",
    });

    if (url === null) {
        return;
    }

    insertEditorImageBlock(url);
}
