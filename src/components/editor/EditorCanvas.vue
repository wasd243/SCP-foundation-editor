<script setup lang="ts">
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";

const editor = useEditor({
  extensions: [StarterKit],
  content: "<p>Hello FTML editor.</p>",
});
</script>

<template>
  <main class="editor-canvas editor-theme-default">
    <EditorContent :editor="editor" />
  </main>
</template>

<style scoped>
.editor-canvas {
  min-height: calc(100vh - 105px);
  padding: 32px 0;
  background: #f2f3f5;
}

:deep(.ProseMirror) {
  width: min(900px, calc(100vw - 96px));
  min-height: 720px;
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
