<!--ContextMenu.vue is for right click context menu-->

<script setup lang="ts">
import { computed } from "vue";
import { getEditor } from "../../stores/editor.ts";
import DefaultContextMenu from "./ContextMenu/DefaultContextMenu.vue";
import TableContextMenu from "./ContextMenu/TableContextMenu.vue";
import TabViewContextMenu from "./ContextMenu/TabViewContextMenu.vue";

defineProps<{
  x: number;
  y: number;
}>();

const isTableMenu = computed(() => getEditor()?.isActive("table") ?? false);

const isTabViewMenu = computed(() => {
  const editor = getEditor();
  if (!editor) return false;

  const { $from, $to } = editor.state.selection;
  const positions = [$from, $to];

  return positions.some(($pos) => {
    for (let depth = $pos.depth; depth > 0; depth -= 1) {
      if ($pos.node(depth).type.name === "tabView") {
        return true;
      }
    }

    return false;
  });
});
</script>

<template>
  <div
      class="editor-context-menu"
      :style="{
      left: `${x}px`,
      top: `${y}px`,
    }"
  >
    <TabViewContextMenu v-if="isTabViewMenu"/>
    <TableContextMenu v-else-if="isTableMenu"/>
    <DefaultContextMenu v-else/>
  </div>
</template>
