<!--ContextMenu.vue is for right click context menu-->

<script setup lang="ts">
import TableContextMenu from "./ContextMenu/TableContextMenu.vue";
import TabViewContextMenu from "./ContextMenu/TabViewContextMenu.vue";
import DefaultContextMenu from "./ContextMenu/DefaultContextMenu.vue";

defineProps<{
  x: number;
  y: number;
  showTabView: boolean;
  showTable: boolean;
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
    <TabViewContextMenu v-if="showTabView"/>
    <DefaultContextMenu v-else/>
    <template v-if="showTable">
      <div v-if="showTabView" class="context-menu-separator"/>
      <TableContextMenu :include-default="!showTabView"/>
    </template>
  </div>
</template>
