import type {JSONContent} from "@tiptap/core";
import type {Node as ProseMirrorNode} from "@tiptap/pm/model";
import type {Transaction} from "@tiptap/pm/state";

import {getEditor} from "../../editor.ts";
import footnoteTemplate from "../../json/footnote.json";

type FootnoteTemplate = {
    reference: JSONContent;
    list: JSONContent;
    orderedList: JSONContent;
    listItem: JSONContent;
};

type PositionedNode = {
    node: ProseMirrorNode;
    pos: number;
};

const footnoteKeyAttributes = [
    "data-footnote-id",
    "footnote-id",
    "data-id",
    "id",
    "href",
];

const templates = footnoteTemplate as FootnoteTemplate;

function cloneTemplate(template: JSONContent, footnoteId: string) {
    return JSON.parse(
        JSON.stringify(template)
            .replaceAll("__FOOTNOTE_ID__", footnoteId),
    ) as JSONContent;
}

function createFootnoteReference(footnoteId: string) {
    return cloneTemplate(templates.reference, footnoteId);
}

function createFootnoteListItem(footnoteId: string) {
    return cloneTemplate(templates.listItem, footnoteId);
}

function createFootnoteOrderedList(footnoteId: string) {
    const orderedList = cloneTemplate(templates.orderedList, footnoteId);

    orderedList.content = [createFootnoteListItem(footnoteId)];

    return orderedList;
}

function createFootnoteList(footnoteId: string) {
    const list = cloneTemplate(templates.list, footnoteId);

    list.content = list.content?.map(child => {
        if (child.attrs?.tagName === "ol") {
            return createFootnoteOrderedList(footnoteId);
        }

        return child;
    });

    return list;
}

function normalizeFootnoteId(value: unknown) {
    if (typeof value !== "string") {
        return null;
    }

    const footnoteId = value.trim().replace(/^#/, "");

    return footnoteId || null;
}

function getHTMLAttributes(attrs: Record<string, unknown>) {
    const htmlAttributes = attrs.htmlAttributes;

    if (htmlAttributes && typeof htmlAttributes === "object") {
        return htmlAttributes as Record<string, unknown>;
    }

    return attrs;
}

function getClassList(attrs: Record<string, unknown>) {
    const className = getHTMLAttributes(attrs).class;

    return typeof className === "string" ? className.split(/\s+/) : [];
}

function hasClass(attrs: Record<string, unknown>, className: string) {
    return getClassList(attrs).includes(className);
}

function nodeHasClass(node: ProseMirrorNode, className: string) {
    return hasClass(node.attrs, className);
}

function getNodeTagName(node: ProseMirrorNode) {
    return typeof node.attrs.tagName === "string" ? node.attrs.tagName : null;
}

function getFootnoteId(attrs: Record<string, unknown>) {
    const htmlAttributes = getHTMLAttributes(attrs);

    for (const attribute of footnoteKeyAttributes) {
        const footnoteId = normalizeFootnoteId(htmlAttributes[attribute]);

        if (footnoteId) {
            return footnoteId;
        }
    }

    return null;
}

function getNextFootnoteId() {
    const editor = getEditor();
    let maxFootnoteId = 0;

    editor?.state.doc.descendants(node => {
        if (
            !hasClass(node.attrs, "wj-footnote-ref-marker") &&
            !hasClass(node.attrs, "wj-footnote-list-item")
        ) {
            return true;
        }

        const footnoteId = getFootnoteId(node.attrs) ?? node.textContent.trim().replace(/\.$/, "");
        const numericFootnoteId = Number.parseInt(footnoteId, 10);

        if (Number.isFinite(numericFootnoteId)) {
            maxFootnoteId = Math.max(maxFootnoteId, numericFootnoteId);
        }

        return true;
    });

    return String(maxFootnoteId + 1);
}

function findTopLevelFootnoteList(doc: ProseMirrorNode): PositionedNode | null {
    let offset = 0;

    for (let index = 0; index < doc.childCount; index += 1) {
        const node = doc.child(index);

        if (nodeHasClass(node, "wj-footnote-list")) {
            return {node, pos: offset};
        }

        offset += node.nodeSize;
    }

    return null;
}

function findDescendantByTagName(node: ProseMirrorNode, tagName: string, basePos: number): PositionedNode | null {
    let offset = 0;

    for (let index = 0; index < node.childCount; index += 1) {
        const child = node.child(index);
        const childPos = basePos + offset + 1;

        if (getNodeTagName(child) === tagName) {
            return {node: child, pos: childPos};
        }

        const descendant = findDescendantByTagName(child, tagName, childPos);

        if (descendant) {
            return descendant;
        }

        offset += child.nodeSize;
    }

    return null;
}

function findFootnoteOrderedList(footnoteList: PositionedNode): PositionedNode | null {
    return findDescendantByTagName(footnoteList.node, "ol", footnoteList.pos);
}

function moveFootnoteListToBottom(doc: ProseMirrorNode, tr: Transaction) {
    const footnoteList = findTopLevelFootnoteList(doc);

    if (!footnoteList) {
        return;
    }

    const from = footnoteList.pos;
    const to = from + footnoteList.node.nodeSize;

    if (to === doc.content.size) {
        return;
    }

    tr.delete(from, to);
    tr.insert(tr.doc.content.size, footnoteList.node);
}

function upsertFootnoteListItem(footnoteId: string) {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const {state, view} = editor;
    const bookmark = state.selection.getBookmark();
    const tr = state.tr;
    const footnoteList = findTopLevelFootnoteList(tr.doc);

    if (!footnoteList) {
        tr.insert(
            tr.doc.content.size,
            state.schema.nodeFromJSON(createFootnoteList(footnoteId)),
        );
    } else {
        const orderedList = findFootnoteOrderedList(footnoteList);

        if (orderedList) {
            tr.insert(
                orderedList.pos + orderedList.node.nodeSize - 1,
                state.schema.nodeFromJSON(createFootnoteListItem(footnoteId)),
            );
        } else {
            tr.insert(
                footnoteList.pos + footnoteList.node.nodeSize - 1,
                state.schema.nodeFromJSON(createFootnoteOrderedList(footnoteId)),
            );
        }
    }

    moveFootnoteListToBottom(tr.doc, tr);
    tr.setSelection(bookmark.map(tr.mapping).resolve(tr.doc));
    view.dispatch(tr);
}

export function insertEditorFootnote() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const footnoteId = getNextFootnoteId();
    const inserted = editor
        .chain()
        .focus()
        .insertContent(createFootnoteReference(footnoteId))
        .run();

    if (inserted) {
        upsertFootnoteListItem(footnoteId);
    }
}
