<script setup lang="ts">
import AddTab from "./TabViewContextMenu/AddTab.vue";
import DeleteTabView from "./TabViewContextMenu/DeleteTabView.vue";
import { addTabEditor } from "../../../stores/btnContextMenu/TabView/btnAddTab.ts";
import { deleteEditorTabView } from "../../../stores/btnContextMenu/TabView/btnDeleteTabView.ts";

function addTab() {
  addTabEditor();
}

function deleteTabView() {
  deleteEditorTabView();
}
</script>

<template>
  <div class="table-context-menu">
    <AddTab @click-command="addTab"/>
    <div class="context-menu-separator"></div>
    <DeleteTabView @click-command="deleteTabView"/>
  </div>
</template>
