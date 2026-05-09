<script setup lang="ts">
import DefaultContextMenu from "./ContextMenu/DefaultContextMenu.vue";

defineProps<{
  x: number;
  y: number;
}>();
</script>

<template>
  <div
      class="editor-context-menu"
      :style="{
      left: `${x}px`,
      top: `${y}px`,
    }"
  >
  <DefaultContextMenu/>
  </div>
</template>
