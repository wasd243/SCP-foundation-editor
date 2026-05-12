<script setup lang="ts">
import AddTab from "./TabViewContextMenu/AddTab.vue";
import DeleteTabView from "./TabViewContextMenu/DeleteTabView.vue";
// All connection should be done with TabView.ts
import { addTabInTipTapEditor } from "../../../stores/btnContextMenu/TabView.ts";
import { deleteTabViewInTipTapEditor} from "../../../stores/btnContextMenu/TabView.ts";

function addTabInEditor() {
  addTabInTipTapEditor();
}

function deleteTabView() {
  deleteTabViewInTipTapEditor();
}
</script>

<template>
  <div class="table-context-menu">
    <AddTab @click-command="addTabInEditor"/>
    <div class="context-menu-separator"></div>
    <DeleteTabView @click-command="deleteTabView"/>
  </div>
</template>
