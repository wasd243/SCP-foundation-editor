<!--RenderSyncHtmlToEditor.vue is used for plugin ftml output HTML into editor-->
<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";
import { getEditor } from "../../../../stores/editor.ts";

function renderSyncHTMLToEditor(event: Event) {
    const html = (event as CustomEvent<string>).detail;
    getEditor()?.commands.setContent(html);
}

onMounted(() => {
    window.addEventListener("code-view-parser-html", renderSyncHTMLToEditor);
});

onBeforeUnmount(() => {
    window.removeEventListener("code-view-parser-html", renderSyncHTMLToEditor);
});
</script>

<template></template>
