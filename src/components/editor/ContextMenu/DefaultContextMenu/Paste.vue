<script setup lang="ts">
import { getEditor } from "../../../../stores/editor";

async function pasteText() {
  const text = await navigator.clipboard.readText();

  getEditor()
      ?.chain()
      .focus()
      .insertContent(text)
      .run();
}
</script>

<template>
  <button
      class="context-menu-item"
      @click="pasteText"
  >
    <span>Paste</span>
    <span class="context-menu-shortcut">Ctrl+V</span>
  </button>
</template>
