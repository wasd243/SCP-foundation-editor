<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { EditorView } from '@codemirror/view';
import { initDivEditor, InsertDiv } from "../../../../stores/btnToolBar/btnInsertion/btnInsertDiv.ts";
import { getEditor } from "../../../../stores/editor/instance.ts";

const editorRef = ref<HTMLElement>();
let view: EditorView | null = null;

onMounted(async () => {
  if (editorRef.value) {
    view = await initDivEditor(editorRef.value);
  }
});

onUnmounted(() => {
  view?.destroy();
});

function InsertDivInEditor() {
  const editor = getEditor();
  if (!view || !editor) return;
  InsertDiv(view, editor);
}
</script>

<template>
  <div class="div-panel">
    <div class="div-panel-header">
      <span style="color: white">Div Block</span>
      <button class="div-panel-header close-button" @click="$emit('close')">
        ✕
      </button>
    </div>
    <div ref="editorRef" class="div-editor-container"/>
    <button class="insert-button" @click="InsertDivInEditor">Insert</button>
  </div>
</template>

<style scoped lang="scss">
.div-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  background: #282c34;
  animation: slide-in 0.2s ease;
  display: flex;
  flex-direction: column;

  &-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;

    .close-button {
      align-self: flex-end;
      margin: 8px 12px;
      padding: 6px 16px;
      background: #3a3f4b;
      color: white;
      border: 1px solid #555;
      border-radius: 4px;
      cursor: pointer;

      &:hover {
        background: #4a5060;
      }
    }
  }

  .div-editor-container {
    overflow: hidden;
  }
}

.insert-button {
  align-self: flex-end;
  margin: 8px 12px;
  padding: 6px 16px;
  background: #3a3f4b;
  color: white;
  border: 1px solid #555;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background: #4a5060;
  }
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}
</style>
