<script setup lang="ts">
import { insertEditorFootnote } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnFootnote.ts";
</script>

<template>
  <button
      class="context-menu-item"
      type="button"
      @click="insertEditorFootnote"
  >
    <span>Footnote</span>
  </button>
</template>
