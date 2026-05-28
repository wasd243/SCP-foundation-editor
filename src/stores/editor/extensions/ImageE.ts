import Image, {type ImageOptions} from "@tiptap/extension-image";
import {mergeAttributes} from "@tiptap/core";
import type {DOMOutputSpec} from "@tiptap/pm/model";
import {Plugin, PluginKey} from "@tiptap/pm/state";
import type {EditorView} from "@tiptap/pm/view";
import {createDeleteImageBlockPlugin} from "./deleteImageBlockE";
import { findTopImageContainer, isImageContainerElement } from "./ImageAttrE";
import {ref} from "vue";

type HTMLAttributes = Record<string, string>;
type RenderAttributes = Record<string, unknown>;

const wrapperAttributeName = "wrapperAttributes";
const imageAttributeName = "imageAttributes";
const removedAttributeRegex = /^crossorigin$/i;
const imageMoveableTargetKey = new PluginKey("imageMoveableTarget");

function getElementAttributes(element: HTMLElement): HTMLAttributes {
    return Object.fromEntries(
        Array.from(element.attributes)
            .filter(attribute => !removedAttributeRegex.test(attribute.name))
            .map(attribute => [attribute.name, attribute.value]),
    );
}

function isAllowedImage(element: HTMLElement, allowBase64: boolean) {
    if (!(element instanceof HTMLImageElement)) {
        return false;
    }

    const src = element.getAttribute("src");

    return Boolean(src) && (allowBase64 || !src?.startsWith("data:"));
}

function findWrappedImage(element: HTMLElement, allowBase64: boolean) {
    if (!(element instanceof HTMLDivElement)) {
        return null;
    }

    if (element.parentElement?.classList.contains("image-container")) {
        return null;
    }

    const children = Array.from(element.children);

    if (children.length !== 1 || !isAllowedImage(children[0] as HTMLElement, allowBase64)) {
        return null;
    }

    const hasText = Array.from(element.childNodes).some(node =>
        node.nodeType === 3 && node.textContent?.trim(),
    );

    return hasText ? null : children[0] as HTMLImageElement;
}

function createImageNodeAttributes(image: HTMLImageElement, wrapperAttributes: HTMLAttributes | null = null) {
    const imageAttributes = getElementAttributes(image);

    return {
        src: imageAttributes.src ?? null,
        alt: imageAttributes.alt ?? null,
        title: imageAttributes.title ?? null,
        width: imageAttributes.width ?? null,
        height: imageAttributes.height ?? null,
        [imageAttributeName]: imageAttributes,
        [wrapperAttributeName]: wrapperAttributes,
    };
}

function objectAttributes(value: unknown): RenderAttributes {
    if (!value || typeof value !== "object" || Array.isArray(value)) {
        return {};
    }

    return value as RenderAttributes;
}

function getRenderableImageAttributes(attributes: RenderAttributes) {
    return Object.fromEntries(
        Object.entries(attributes).filter(([name, value]) =>
            name !== wrapperAttributeName &&
            name !== imageAttributeName &&
            value !== null &&
            value !== undefined,
        ),
    );
}

function hasWrapper(value: unknown) {
    return value !== null && value !== undefined;
}

export const selectedImageBlockElement = ref<HTMLElement | null>(null);

function isProseMirrorHackImage(element: HTMLElement) {
    return element.tagName.toLowerCase() === "img" &&
        (
            element.classList.contains("ProseMirror-separator") ||
            element.hasAttribute("mark-placeholder") ||
            !element.hasAttribute("src")
        );
}

function updateMoveableTarget(view: EditorView) {
    const selected = view.dom.querySelector("img.ProseMirror-selectednode");

    if (selected instanceof HTMLElement) {
        if (isProseMirrorHackImage(selected)) {
            selectedImageBlockElement.value = null;
            return;
        }

        selectedImageBlockElement.value = findTopImageContainer(selected) ?? selected;
        return;
    }

    if (
        selectedImageBlockElement.value &&
        view.dom.contains(selectedImageBlockElement.value) &&
        isImageContainerElement(selectedImageBlockElement.value)
    ) {
        return;
    }

    selectedImageBlockElement.value = null;
}

function updateMoveableTargetFromPointerDown(_view: EditorView, event: Event) {
    const target = event.target;

    if (!(target instanceof HTMLElement)) {
        selectedImageBlockElement.value = null;
        return false;
    }

    if (isProseMirrorHackImage(target)) {
        selectedImageBlockElement.value = null;
        return false;
    }

    selectedImageBlockElement.value = findTopImageContainer(target);
    return false;
}

function createImageMoveableTargetPlugin() {

    console.log("[ImageE] createImageMoveableTargetPlugin Active");

    return new Plugin({
        key: imageMoveableTargetKey,
        props: {
            handleDOMEvents: {
                pointerdown: updateMoveableTargetFromPointerDown,
            },
        },
        view(view) {
            updateMoveableTarget(view);

            return {
                update: updateMoveableTarget,
                destroy() {
                    selectedImageBlockElement.value = null;
                },
            };
        },
    });
}

export const ImageExtension = Image.extend<ImageOptions>({
    priority: 1100,

    addAttributes() {
        return {
            ...(this.parent?.() ?? {}),
            [wrapperAttributeName]: {
                default: null,
            },
            [imageAttributeName]: {
                default: {},
            },
        };
    },

    parseHTML() {
        const imageSelector = this.options.allowBase64
            ? "img[src]"
            : 'img[src]:not([src^="data:"])';

        return [
            {
                tag: "div",
                priority: 1100,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement)) {
                        return false;
                    }

                    const image = findWrappedImage(element, this.options.allowBase64);

                    return image
                        ? createImageNodeAttributes(image, getElementAttributes(element))
                        : false;
                },
            },
            {
                tag: imageSelector,
                getAttrs: element => {
                    if (!(element instanceof HTMLElement) || !isAllowedImage(element, this.options.allowBase64)) {
                        return false;
                    }

                    return createImageNodeAttributes(element as HTMLImageElement);
                },
            },
        ];
    },

    renderHTML({ HTMLAttributes }): DOMOutputSpec {
        const rawWrapperAttributes = HTMLAttributes[wrapperAttributeName];
        const wrapperAttributes = objectAttributes(rawWrapperAttributes);
        const imageAttributes = mergeAttributes(
            this.options.HTMLAttributes,
            objectAttributes(HTMLAttributes[imageAttributeName]),
            getRenderableImageAttributes(HTMLAttributes),
        );
        const image: DOMOutputSpec = ["img", imageAttributes];

        if (hasWrapper(rawWrapperAttributes)) {
            return ["div", wrapperAttributes, image];
        }

        return image;
    },

    addProseMirrorPlugins() {
        return [
            ...(this.parent?.() ?? []),
            createDeleteImageBlockPlugin(),
            createImageMoveableTargetPlugin(),
        ];
    },
});
