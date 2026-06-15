<script setup lang="ts">
import { ref } from "vue";
import { DOMSerializer } from "@tiptap/pm/model";

import { getEditor } from "../../../../stores/editor/instance.ts";
import { collectFootnoteDocumentInfo } from "../../../../stores/editor/extensions/WJtags/FootnoteE.ts";
import { useEditorSubscription } from "../../../../composables/useEditorSubscription.ts";

type FootnoteEntry = {
    key: string | null;
    html: string;
};

const footnotes = ref<FootnoteEntry[]>([]);

// Mirror every `wj-footnote-list-item-contents` node from the document into the panel.
function syncFootnotes() {
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
</script>

<template>
    <div class="footnote-edit-panel">
        <h1>Footnotes</h1>
        <div class="wj-footnote-list-wrapper">
            <p v-if="footnotes.length === 0" class="footnote-empty">
                No footnotes yet.
            </p>
            <ol v-else class="wj-footnote-list">
                <li
                    v-for="(footnote, index) in footnotes"
                    :key="footnote.key ?? index"
                    class="wj-footnote-list-item-contents"
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

            // wrapper <li> is the contents node; clear any inherited footnote layout
            &.wj-footnote-list-item-contents
                display: list-item

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
