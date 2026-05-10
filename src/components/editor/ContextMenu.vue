<!--ContextMenu.vue is for right click context menu-->

<script setup lang="ts">
import { computed } from "vue";
import { getEditor } from "../../stores/editor.ts";
import DefaultContextMenu from "./ContextMenu/DefaultContextMenu.vue";
import TableContextMenu from "./ContextMenu/TableContextMenu.vue";

defineProps<{
  x: number;
  y: number;
}>();

const isTableMenu = computed(() => getEditor()?.isActive("table") ?? false);
</script>

<template>
  <div
      class="editor-context-menu"
      :style="{
      left: `${x}px`,
      top: `${y}px`,
    }"
  >
    <TableContextMenu v-if="isTableMenu"/>
    <DefaultContextMenu v-else/>
  </div>
</template>
