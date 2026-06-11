<script setup lang="ts">
import {ref, onMounted, onUnmounted} from 'vue';
import {EditorView} from '@codemirror/view';
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
      <span style="color: white">Module CSS</span>
      <button class="css-panel-header close-button" @click="$emit('close')">
        ✕
      </button>
    </div>
    <div ref="editorRef" class="css-editor-container"/>
    <button class="inject-button" @click="SaveCSSinEditor">Inject</button>
  </div>
</template>

<style scoped lang="scss">
.css-panel {
  position: fixed;
  right: 0;
  top: 0;
  height: 100%;
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

    // The close button use same style as inject button.
    // Why not define it in parent container?
    // Because I'm lazy.
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

  .css-editor-container {
    flex: 1;
    overflow: auto;
  }
}

// The close button use same style as inject button.
// Why not define it in parent container?
// Because I'm lazy.
.inject-button {
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
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>
