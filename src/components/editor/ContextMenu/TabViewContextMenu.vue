<script setup lang="ts">
import DefaultContextMenu from "./DefaultContextMenu.vue";
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
    <DefaultContextMenu/>
    <div class="context-menu-separator"></div>
    <AddTab @click-command="addTabInEditor"/>
    <DeleteTabView @click-command="deleteTabView"/>
  </div>
</template>
