<script setup lang="ts">
import DeleteTabView from "./TabViewContextMenu/DeleteTabView.vue";
import { deleteEditorTabView } from "../../../stores/btnContextMenu/TabView/btnDeleteTabView.ts";

function deleteTabView() {
  deleteEditorTabView();
}
</script>

<template>
  <div class="table-context-menu">
    <DeleteTabView @click-command="deleteTabView"/>
  </div>
</template>
