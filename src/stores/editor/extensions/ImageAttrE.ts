import type {Editor} from "@tiptap/core";
import type {Node as ProseMirrorNode} from "@tiptap/pm/model";
import type {Transaction} from "@tiptap/pm/state";

import {getEditor} from "../../editor.ts";

export type ImagePosition = "left" | "center" | "right";
export type PlainImageFlow = "inline" | "wrap";

export const imageAlignmentClasses = ["alignleft", "alignright", "aligncenter"];
export const imageFloatPositionClasses = ["floatleft", "floatright"];
export const imagePositionClasses = [...imageAlignmentClasses, ...imageFloatPositionClasses];

type AttributeName = "htmlAttributes" | "wrapperAttributes";

function isObjectAttributes(value: unknown): value is Record<string, unknown> {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function getImageContainerAttributeName(node: ProseMirrorNode): AttributeName | null {
    if (isObjectAttributes(node.attrs.htmlAttributes)) {
        return "htmlAttributes";
    }

    if (isObjectAttributes(node.attrs.wrapperAttributes)) {
        return "wrapperAttributes";
    }

    return null;
}

function setStyleSize(styleText: unknown, width: string, height: string) {
    const element = document.createElement("div");

    element.style.cssText = typeof styleText === "string" ? styleText : "";
    element.style.width = width;
    element.style.height = height;

    return element.style.cssText;
}

function setImageElementSizeAttributes(attributes: Record<string, unknown>, width: string, height: string) {
    const imageAttributes = isObjectAttributes(attributes.imageAttributes)
        ? attributes.imageAttributes
        : {};

    return {
        ...attributes,
        width,
        height,
        imageAttributes: {
            ...imageAttributes,
            style: setStyleSize(imageAttributes.style, width, height),
        },
    };
}

function setStyleMargin(styleText: unknown, margin: string | null) {
    const element = document.createElement("div");

    element.style.cssText = typeof styleText === "string" ? styleText : "";
    element.style.margin = margin ?? "";

    return element.style.cssText;
}

function splitClassName(className: unknown) {
    return typeof className === "string" ? className.split(/\s+/).filter(Boolean) : [];
}

function getImageContainerClassName(className: unknown, positionClass: string | null) {
    const classNames = splitClassName(className)
        .filter(className => !imagePositionClasses.includes(className));

    if (positionClass) {
        classNames.push(positionClass);
    }

    return classNames.join(" ");
}

function nodeHasImageContainerAttrs(node: ProseMirrorNode) {
    const attrsName = getImageContainerAttributeName(node);

    if (!attrsName) {
        return false;
    }

    const attributes = node.attrs[attrsName] as Record<string, unknown>;

    return splitClassName(attributes.class).includes("image-container");
}

function cleanNestedImageWrapperNodeAttrs(transaction: Transaction) {
    function scanNode(node: ProseMirrorNode, position: number, insideImageContainer: boolean) {
        node.forEach((child, offset) => {
            const childPosition = position + 1 + offset;
            const childHasImageContainer = nodeHasImageContainerAttrs(child);

            if (insideImageContainer && isObjectAttributes(child.attrs.wrapperAttributes)) {
                transaction.setNodeMarkup(childPosition, undefined, {
                    ...child.attrs,
                    wrapperAttributes: null,
                }, child.marks);
            }

            scanNode(child, childPosition, insideImageContainer || childHasImageContainer);
        });
    }

    transaction.doc.forEach((node, offset) => {
        scanNode(node, offset, nodeHasImageContainerAttrs(node));
    });
}

function patchImageContainerNodeAttrs(
    container: HTMLElement,
    patchAttributes: (attributes: Record<string, unknown>, node: ProseMirrorNode) => Record<string, unknown>,
) {
    const editor = getEditor();
    const targetContainer = findTopImageContainer(container) ?? container;
    const position = editor ? findNodePositionByElement(editor, targetContainer) : null;

    if (!editor || position === null) {
        return false;
    }

    const node = editor.state.doc.nodeAt(position);

    if (!node) {
        return false;
    }

    const attrsName = getImageContainerAttributeName(node);

    if (!attrsName) {
        return false;
    }

    const attributes = node.attrs[attrsName] as Record<string, unknown>;
    const transaction = editor.state.tr;

    transaction.setNodeMarkup(position, undefined, {
        ...node.attrs,
        [attrsName]: patchAttributes({ ...attributes }, node),
    }, node.marks);
    cleanNestedImageWrapperNodeAttrs(transaction);
    editor.view.dispatch(transaction);

    return true;
}

export function isImageContainerElement(element: HTMLElement) {
    return element.tagName.toLowerCase() === "div" && element.classList.contains("image-container");
}

export function findTopImageContainer(element: HTMLElement) {
    let current: HTMLElement | null = element;
    let imageContainer: HTMLElement | null = null;

    while (current) {
        if (isImageContainerElement(current)) {
            imageContainer = current;
        }

        current = current.parentElement;
    }

    return imageContainer;
}

export function findNodePositionByElement(editor: Editor, element: HTMLElement) {
    let position: number | null = null;

    editor.state.doc.descendants((_node, pos) => {
        if (editor.view.nodeDOM(pos) === element) {
            position = pos;
            return false;
        }

        return true;
    });

    return position;
}

export function getImagePositionClass(container: HTMLElement, position: ImagePosition) {
    if (container.hasAttribute("data-editor-include")) {
        return position === "left" ? "alignleft" : position === "right" ? "alignright" : "aligncenter";
    }

    return position === "left" ? "floatleft" : position === "right" ? "floatright" : "aligncenter";
}

export function getImagePositionMargin(position: ImagePosition) {
    return position === "left"
        ? "0 1em 0.8em 0"
        : position === "right"
            ? "0 0 0.8em 1em"
            : "0 auto 0.8em auto";
}

export function clearNestedImageContainerDom(container: HTMLElement) {
    container.querySelectorAll("div.image-container").forEach(child => {
        imagePositionClasses.forEach(className => child.classList.remove(className));
        child.classList.remove("image-container");

        if (child instanceof HTMLElement) {
            child.style.transform = "";
            child.style.margin = "";
        }
    });
}

export function setImageContainerPositionDom(container: HTMLElement, position: ImagePosition) {
    imagePositionClasses.forEach(className => container.classList.remove(className));
    clearNestedImageContainerDom(container);

    container.classList.add(getImagePositionClass(container, position));
    container.style.transform = "";
    container.style.margin = getImagePositionMargin(position);
}

export function setPlainImageFlowDom(container: HTMLElement, flow: PlainImageFlow) {
    imagePositionClasses.forEach(className => container.classList.remove(className));
    clearNestedImageContainerDom(container);
    container.style.transform = "";
    container.style.margin = "";

    if (flow === "wrap") {
        container.classList.add("floatleft");
    }
}

export function syncImageContainerSizeDom(container: HTMLElement, width: string, height: string) {
    const img = container.querySelector("img") as HTMLElement | null;

    container.style.width = width;
    container.style.height = height;

    if (!img) {
        return;
    }

    img.style.width = width;
    img.style.height = height;
}

export function updateImageContainerSizeAttrs(container: HTMLElement, width: string, height: string) {
    return patchImageContainerNodeAttrs(container, attributes => ({
        ...attributes,
        style: setStyleSize(attributes.style, width, height),
    }));
}

export function updateImageElementSizeAttrs(image: HTMLElement, width: string, height: string) {
    const editor = getEditor();
    const position = editor ? findNodePositionByElement(editor, image) : null;

    if (!editor || position === null) {
        return false;
    }

    const node = editor.state.doc.nodeAt(position);

    if (!node || node.type.name !== "image") {
        return false;
    }

    editor.view.dispatch(
        editor.state.tr.setNodeMarkup(
            position,
            undefined,
            setImageElementSizeAttributes(node.attrs, width, height),
            node.marks,
        ),
    );

    return true;
}

export function updateImageContainerPositionAttrs(container: HTMLElement, position: ImagePosition) {
    const positionClass = getImagePositionClass(container, position);
    const margin = getImagePositionMargin(position);

    return patchImageContainerNodeAttrs(container, attributes => ({
        ...attributes,
        class: getImageContainerClassName(attributes.class, positionClass),
        style: setStyleMargin(attributes.style, margin),
    }));
}

export function updatePlainImageFlowAttrs(container: HTMLElement, flow: PlainImageFlow) {
    return patchImageContainerNodeAttrs(container, attributes => {
        const nextAttributes: Record<string, unknown> = {
            ...attributes,
            class: getImageContainerClassName(attributes.class, flow === "wrap" ? "floatleft" : null),
            style: setStyleMargin(attributes.style, null),
        };

        if (!nextAttributes.class) {
            delete nextAttributes.class;
        }

        if (!nextAttributes.style) {
            delete nextAttributes.style;
        }

        return nextAttributes;
    });
}
