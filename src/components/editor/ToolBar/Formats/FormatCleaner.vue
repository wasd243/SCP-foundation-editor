<script setup lang="ts">
import FormatCleaner from "../../../../assets/icons/FormatCleaner.svg";
import { getEditor } from "../../../../stores/editor/instance.ts";
import { clearFootnoteMarks } from "../../../../stores/editor/extensions/WJtags/footnoteActiveView.ts";

function formatCleaner() {
    if (clearFootnoteMarks()) return;

    const editor = getEditor();
    if (!editor) return;

    const state = editor.state;
    if (state.selection.empty) {
        editor.view.dispatch(state.tr.setStoredMarks([]));
    } else {
        editor.chain().focus().unsetAllMarks().run();
    }
}
</script>

<template>
    <button
        class="format-basic-button format-cleaner"
        type="button"
        @click="formatCleaner"
    >
        <img :src="FormatCleaner" alt="Format Cleaner" />
    </button>
</template>

<style scoped lang="sass">
.format-basic-button.format-cleaner
    position: absolute
    width: 28px
    height: 28px
    left: calc(var(--basic-btn-left) + 620px)
    top: calc(var(--basic-btn-height) + 5px)
    img
        // Because of the svg size
        min-width: 200%
        min-height: 200%
</style>
