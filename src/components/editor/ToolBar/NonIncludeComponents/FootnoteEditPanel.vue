<script setup lang="ts">
import { ref } from "vue";
import {
    DOMParser as PMDOMParser,
    DOMSerializer,
    Fragment,
    type Node as ProseMirrorNode,
} from "@tiptap/pm/model";

import { getEditor } from "../../../../stores/editor/instance.ts";
import {
    collectFootnoteDocumentInfo,
    type FootnoteContentNode,
} from "../../../../stores/editor/extensions/WJtags/FootnoteE.ts";
import { useEditorSubscription } from "../../../../composables/useEditorSubscription.ts";

type FootnoteEntry = {
    key: string | null;
    html: string;
};

const footnotes = ref<FootnoteEntry[]>([]);

// While the user edits inside the panel, pause `syncFootnotes` so document
// updates never re-render the `<li>` they are typing in and drop the caret.
const isEditing = ref(false);

// Mirror every `wj-footnote-list-item-contents` node from the document into the panel.
function syncFootnotes() {
    if (isEditing.value) {
        return;
    }

    const editor = getEditor();

    if (!editor) {
        footnotes.value = [];
        return;
    }

    const serializer = DOMSerializer.fromSchema(editor.schema);
    const { sources } = collectFootnoteDocumentInfo(editor.state.doc);

    footnotes.value = sources.map((source) => {
        const fragment = serializer.serializeFragment(source.node.content);
        const wrapper = document.createElement("div");

        wrapper.appendChild(fragment);

        return { key: source.key, html: wrapper.innerHTML };
    });
}

useEditorSubscription(syncFootnotes);

// Convert edited panel HTML back into inline ProseMirror content.
function parseInlineFragment(
    schema: ProseMirrorNode["type"]["schema"],
    element: HTMLElement,
) {
    const slice = PMDOMParser.fromSchema(schema).parseSlice(element, {
        preserveWhitespace: true,
    });
    const inlineNodes: ProseMirrorNode[] = [];

    slice.content.forEach((node) => {
        if (node.isText || node.isInline) {
            inlineNodes.push(node);
            return;
        }

        // `Enter` is blocked, but contenteditable can still wrap pasted text in
        // a block node; unwrap it so only inline content is written back.
        node.content.forEach((child) => inlineNodes.push(child));
    });

    return Fragment.fromArray(inlineNodes);
}

// Match by data-id first so an edit never lands on the wrong footnote; fall
// back to panel order only when a footnote has no id.
function findSource(
    sources: FootnoteContentNode[],
    key: string | null,
    index: number,
) {
    if (key) {
        const matched = sources.find((source) => source.key === key);

        if (matched) {
            return matched;
        }
    }

    return sources[index] ?? null;
}

function writeFootnoteContent(
    key: string | null,
    index: number,
    element: HTMLElement,
) {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const { sources } = collectFootnoteDocumentInfo(editor.state.doc);
    const source = findSource(sources, key, index);

    if (!source) {
        return;
    }

    try {
        const fragment = parseInlineFragment(editor.schema, element);
        const transaction = editor.state.tr.replaceWith(
            source.pos + 1,
            source.pos + source.node.nodeSize - 1,
            fragment,
        );

        // FootnoteSyncE propagates this source edit to the in-text references.
        editor.view.dispatch(transaction);
    } catch (error) {
        console.warn("Failed to sync footnote edit back to document.", error);
    }
}

function getListItem(target: EventTarget | null) {
    if (!(target instanceof HTMLElement)) {
        return null;
    }

    return target.closest<HTMLElement>("li.wj-footnote-list-item-contents");
}

function getListItemIndex(wrapper: HTMLElement, item: HTMLElement) {
    return Array.from(
        wrapper.querySelectorAll("li.wj-footnote-list-item-contents"),
    ).indexOf(item);
}

function onPanelFocusIn(event: FocusEvent) {
    if (getListItem(event.target)) {
        isEditing.value = true;
    }
}

function onPanelFocusOut(event: FocusEvent) {
    const wrapper = event.currentTarget as HTMLElement;

    // Keep editing while focus moves between footnote items.
    if (wrapper.contains(event.relatedTarget as Node | null)) {
        return;
    }

    isEditing.value = false;
    syncFootnotes();
}

function onPanelInput(event: Event) {
    const wrapper = event.currentTarget as HTMLElement;
    const item = getListItem(event.target);

    if (!item) {
        return;
    }

    writeFootnoteContent(
        item.dataset.id ?? null,
        getListItemIndex(wrapper, item),
        item,
    );
}

function onPanelKeydown(event: KeyboardEvent) {
    // Footnote contents are single inline block; do not allow line breaks.
    if (event.key === "Enter") {
        event.preventDefault();
    }
}
</script>

<template>
    <div class="footnote-edit-panel">
        <h1>Footnotes</h1>
        <div
            class="wj-footnote-list-wrapper"
            @focusin="onPanelFocusIn"
            @focusout="onPanelFocusOut"
            @input="onPanelInput"
            @keydown="onPanelKeydown"
        >
            <p v-if="footnotes.length === 0" class="footnote-empty">
                No footnotes yet.
            </p>
            <ol v-else class="wj-footnote-list">
                <li
                    v-for="(footnote, index) in footnotes"
                    :key="footnote.key ?? index"
                    class="wj-footnote-list-item-contents"
                    :data-id="footnote.key"
                    contenteditable="true"
                    spellcheck="false"
                    v-html="footnote.html"
                ></li>
            </ol>
        </div>
    </div>
</template>

<style scoped lang="sass">
// Variables - One Dark Theme Colors
$bg-base: #1e1e1e
$bg-editor: #282c34
$bg-scrollbar-track: #21252b
$bg-scrollbar-thumb: #4b5363
$bg-scrollbar-thumb-hover: #5c6370
$border-color: #181a1f
$text-main: #abb2bf
$accent: #61afef

.footnote-edit-panel
    width: 20vw
    height: 100vh
    background-color: $bg-editor
    color: $text-main
    overflow-y: auto
    box-sizing: border-box
    padding: 30px
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace
    font-size: 15px
    line-height: 1.6
    box-shadow: -5px 0 20px rgba(0, 0, 0, 0.4)
    display: flex
    flex-direction: column
    position: fixed
    right: 60px
    top: 380px
    z-index: 9999 // high z-index to make sure user can see it

    .wj-footnote-list-wrapper
        margin-top: 12px

    .footnote-empty
        color: $bg-scrollbar-thumb-hover
        font-style: italic

    .wj-footnote-list
        margin: 0
        padding-left: 1.6em

        li
            margin-bottom: 10px
            word-break: break-word
            cursor: text

            // wrapper <li> is the contents node; clear any inherited footnote layout
            &.wj-footnote-list-item-contents
                display: list-item

            &:focus
                outline: 1px solid $accent
                outline-offset: 3px
                border-radius: 2px

    // Custom Scrollbar
    &::-webkit-scrollbar
        width: 14px

    &::-webkit-scrollbar-track
        background: $bg-scrollbar-track
        border-left: 1px solid $border-color

    &::-webkit-scrollbar-thumb
        background: $bg-scrollbar-thumb
        border: 3px solid $bg-scrollbar-track
        border-radius: 8px

        &:hover
            background: $bg-scrollbar-thumb-hover
</style>
