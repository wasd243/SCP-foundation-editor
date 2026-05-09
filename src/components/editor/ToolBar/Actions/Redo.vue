<script setup lang="ts">
import { redoEditor } from "../../../../stores/btnToolBar/btnActions/btnRedo.ts";
</script>

<template>
  <button class="actions-button redo" type="button" @click="redoEditor">↷</button>
</template>
