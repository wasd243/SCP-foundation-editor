<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { EditorView } from '@codemirror/view';
import {initCSSEditor, SaveCSS} from "../../../../stores/btnToolBar/btnInsertion/btnInsertCSS.ts";

const editorRef = ref<HTMLElement>();
let view: EditorView | null = null;

onMounted(async () => {
  if (editorRef.value) {
    view = await initCSSEditor(editorRef.value);
  }
});

onUnmounted(() => {
  view?.destroy();
});

// Save CSS in editor, use a different function name to avoid conflict with the `SaveCSS` function.
async function SaveCSSinEditor() {
  if (view) await SaveCSS(view);
}
</script>

<template>
  <div class="css-panel">
    <div class="css-panel-header">
      <span>Module CSS</span>
      <button @click="$emit('close')">✕</button>
    </div>
    <div ref="editorRef" class="css-editor-container" />
    <button @click="SaveCSSinEditor">Inject</button>
  </div>
</template>

<style scoped>
.css-panel {
  position: fixed;
  right: 0;
  top: 0;
  height: 100%;
  width: 400px;
  background: #1e1e1e;
  animation: slide-in 0.2s ease;
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}
</style>
