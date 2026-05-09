<script setup lang="ts">
import { undoEditor } from "../../../../stores/btnToolBar/btnActions/btnUndo.ts";
</script>

<template>
  <button class="actions-button undo" type="button" @click="undoEditor">↶</button>
</template>
