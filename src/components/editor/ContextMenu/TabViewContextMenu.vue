<script setup lang="ts">
import AddTab from "./TabViewContextMenu/AddTab.vue";
import DeleteTabView from "./TabViewContextMenu/DeleteTabView.vue";
// All connection should be done with TabView.ts
import { addTabInTipTapEditor } from "../../../stores/btnContextMenu/TabView.ts";
import { deleteEditorTabView } from "../../../stores/btnContextMenu/TabView/btnDeleteTabView.ts";

function addTabInEditor() {
  addTabInTipTapEditor();
}

function deleteTabView() {
  deleteEditorTabView();
}
</script>

<template>
  <div class="table-context-menu">
    <AddTab @click-command="addTabInEditor"/>
    <div class="context-menu-separator"></div>
    <DeleteTabView @click-command="deleteTabView"/>
  </div>
</template>
