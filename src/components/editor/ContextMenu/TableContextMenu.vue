<script setup lang="ts">
import DefaultContextMenu from "./DefaultContextMenu.vue";
import AddColumn from "./TableContextMenu/AddColumn.vue";
import AddRow from "./TableContextMenu/AddRow.vue";
import DeleteColumn from "./TableContextMenu/DeleteColumn.vue";
import DeleteRow from "./TableContextMenu/DeleteRow.vue";
import DeleteTable from "./TableContextMenu/DeleteTable.vue";
import { addTableColumnEditor } from "../../../stores/btnContextMenu/table/btnAddColumn.ts";
import { addTableRowEditor } from "../../../stores/btnContextMenu/table/btnAddRow.ts";
import { deleteTableColumnEditor } from "../../../stores/btnContextMenu/table/btnDeleteColumn.ts";
import { deleteTableRowEditor } from "../../../stores/btnContextMenu/table/btnDeleteRow.ts";
import { deleteEditorTable } from "../../../stores/btnContextMenu/table/btnDeleteTable.ts";

function addColumn() {
  addTableColumnEditor();
}

function addRow() {
  addTableRowEditor();
}

function deleteColumn() {
  deleteTableColumnEditor();
}

function deleteRow() {
  deleteTableRowEditor();
}

function deleteTable() {
  deleteEditorTable();
}

defineProps<{
  includeDefault?: boolean;
}>();
</script>

<template>
  <div class="table-context-menu">
    <AddColumn @click-command="addColumn"/>
    <AddRow @click-command="addRow"/>
    <div class="context-menu-separator"></div>
    <DeleteColumn @click-command="deleteColumn"/>
    <DeleteRow @click-command="deleteRow"/>
    <div class="context-menu-separator"></div>
    <DeleteTable @click-command="deleteTable"/>
  </div>
</template>
