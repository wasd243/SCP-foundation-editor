<script setup lang="ts">
import OrderedList from "./List/OrderedList.vue";
import UnorderedList from "./List/UnorderedList.vue";
import { toggleOrderedListEditor } from "../../../../stores/btnToolBar/btnFormats/btnList/btnOrderedList.ts";
import { toggleUnorderedListEditor } from "../../../../stores/btnToolBar/btnFormats/btnList/btnUnorderedList.ts";

function toggleOrderedList() {
  toggleOrderedListEditor();
}

function toggleUnorderedList() {
  toggleUnorderedListEditor();
}

function listIdleInterface() {}

defineExpose({
  listIdleInterface,
});
</script>

<template>
  <OrderedList @toggle="toggleOrderedList"/>
  <UnorderedList @toggle="toggleUnorderedList"/>
</template>
