<script setup lang="ts">
import { ref } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import { editorExtensions, getEditor, setEditor } from "../../stores/editor.ts";
import ContextMenu from "./ContextMenu.vue";

const contextMenuVisible = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);

function handleContextMenu(event: MouseEvent) {
  event.preventDefault();

  const editorInstance = getEditor();
  const position = editorInstance?.view.posAtCoords({
    left: event.clientX,
    top: event.clientY,
  });

  if (editorInstance && position && Number.isInteger(position.pos)) {
    const docSize = editorInstance.state.doc.content.size;

    if (position.pos >= 0 && position.pos <= docSize) {
      try {
        editorInstance.chain().focus().setTextSelection(position.pos).run();
      } catch {
        // Keep the context menu available even when ProseMirror rejects an edge position.
      }
    }
  }

  contextMenuX.value = event.clientX;
  contextMenuY.value = event.clientY;
  contextMenuVisible.value = true;
}

function closeContextMenu() {
  contextMenuVisible.value = false;
}

const editor = useEditor({
  extensions: editorExtensions,
  content: "<p>Hello FTML editor.</p>",

  //@ts-ignore
  onCreate: ({ editor }) => setEditor(editor),
  onDestroy: () => setEditor(null),

  editorProps: {
    handlePaste(view, event) {
      const text = event.clipboardData?.getData("text/plain");

      if (!text) {
        return false;
      }

      event.preventDefault();

      view.dispatch(
          view.state.tr.insertText(text)
      );

      return true;
    },
  },
});

</script>

<template>
  <main
      class="editor-canvas editor-theme-default"
      @contextmenu="handleContextMenu"
      @click="closeContextMenu"
  >
    <EditorContent :editor="editor" />

    <ContextMenu
        v-if="contextMenuVisible"
        :x="contextMenuX"
        :y="contextMenuY"
    />
  </main>
</template>

<style scoped>
.editor-canvas {
  height: calc(100vh - 105px);
  overflow-y: auto;
  padding: 32px 0;
  background: #f2f3f5;
  box-sizing: border-box;
}

:deep(.ProseMirror) {
  width: min(900px, calc(100vw - 96px));
  min-height: 900px;
  margin: 0 auto;
  padding: 48px 56px;
  box-sizing: border-box;

  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);

  outline: none;
}

:deep(.ProseMirror:focus) {
  outline: none;
}
</style>
