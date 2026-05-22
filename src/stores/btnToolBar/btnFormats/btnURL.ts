import {getEditor} from "../../editor.ts";

function normalizeUrl(url: string) {
    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
        return "";
    }

    if (/^(?:[a-z][a-z\d+.-]*:|#|\/)/i.test(trimmedUrl)) {
        return trimmedUrl;
    }

    return `https://${trimmedUrl}`;
}

export function getCurrentEditorLinkHref() {
    const editor = getEditor();

    if (!editor?.isActive("link")) {
        return undefined;
    }

    return editor.getAttributes("link").href as string | undefined;
}

export function insertEditorLink(rawUrl: string) {
    const editor = getEditor();
    const href = normalizeUrl(rawUrl);

    if (!editor || !href) {
        return;
    }

    const { empty } = editor.state.selection;
    const currentHref = editor.getAttributes("link").href as string | undefined;
    const chain = editor.chain().focus();

    if (empty && !currentHref) {
        chain
            .insertContent({
                type: "text",
                text: href,
                marks: [
                    {
                        type: "link",
                        attrs: { href },
                    },
                ],
            })
            .run();
        return;
    }

    chain
        .extendMarkRange("link")
        .setLink({ href })
        .run();
}

export function promptEditorLink() {
    const currentHref = getCurrentEditorLinkHref();
    const url = window.prompt("URL", currentHref ?? "");

    if (url === null) {
        return;
    }

    insertEditorLink(url);
}
