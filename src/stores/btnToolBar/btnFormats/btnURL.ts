import {getEditor} from "../../editor.ts";

// This function is used to normalize URLs which entered by user but without `http` or `https` begin
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

type LinkClass = "active";

type LinkOptions = {
    class?: LinkClass;
    normalize?: boolean;
    leadingSlash?: boolean;
    promptLabel?: string;
};

function createLinkAttributes(href: string, options: LinkOptions = {}) {
    return {
        href,
        ...(options.class ? { class: options.class } : {}),
    };
}

function ensureLeadingSlash(href: string) {
    return href.startsWith("/") ? href : `/${href}`;
}

export function insertEditorLink(rawUrl: string, options: LinkOptions = {}) {
    const editor = getEditor();
    const normalizedHref = options.normalize === false ? rawUrl : normalizeUrl(rawUrl);
    const href = options.leadingSlash ? ensureLeadingSlash(normalizedHref) : normalizedHref;

    if (!editor || !href) {
        return;
    }

    const { empty } = editor.state.selection;
    const currentHref = editor.getAttributes("link").href as string | undefined;
    const chain = editor.chain().focus();

    if (empty && !currentHref) {
        const attrs = createLinkAttributes(href, options);

        chain
            .insertContent({
                type: "text",
                text: href,
                marks: [
                    {
                        type: "link",
                        attrs,
                    },
                ],
            })
            .run();
        return;
    }

    chain
        .extendMarkRange("link")
        .setLink(createLinkAttributes(href, options))
        .run();
}

export function promptEditorLink(options: LinkOptions = {}) {
    const currentHref = getCurrentEditorLinkHref();
    const url = window.prompt(options.promptLabel ?? "Enter URL", currentHref ?? "");

    if (url === null) {
        return;
    }

    insertEditorLink(url, options);
}
