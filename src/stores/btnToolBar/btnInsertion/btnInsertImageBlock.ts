import type { JSONContent } from "@tiptap/core";

import { getEditor } from "../../editor.ts";
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
                type: "wjTextBlockTag",
                attrs: {
                    tagName: "div",
                    htmlAttributes: {
                        class: "scp-image-caption",
                        contenteditable: "true",
                    },
                },
                content: [
                    {
                        type: "text",
                        text: defaultImageBlockCaption,
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

export function promptEditorImageBlock() {
    const url = window.prompt("Enter image URL");

    if (url === null) {
        return;
    }

    insertEditorImageBlock(url);
}
