<script setup lang="ts">
import Larger from "./Size/Larger.vue";
import Smaller from "./Size/Smaller.vue";
import ListSize from "./Size/ListSize.vue";
import ListTitle from "./Size/ListTitle.vue";
import { increaseFontSizeEditor } from "../../../../stores/btnToolBar/btnFormats/btnSize/btnLarger.ts";
import { decreaseFontSizeEditor } from "../../../../stores/btnToolBar/btnFormats/btnSize/btnSmaller.ts";
import { setListFontSizeEditor } from "../../../../stores/btnToolBar/btnFormats/btnSize/btnListSize.ts";
import { setListTitleEditor } from "../../../../stores/btnToolBar/btnFormats/btnSize/btnListTitle.ts";

function increaseFontSize() {
  increaseFontSizeEditor();
}

function decreaseFontSize() {
  decreaseFontSizeEditor();
}

function setFontSize(size: number) {
  setListFontSizeEditor(size);
}

function setTitle(title: string) {
  setListTitleEditor(title);
}

function sizeIdleInterface() {}

defineExpose({
  sizeIdleInterface,
});
</script>

<template>
  <Larger @increase="increaseFontSize"/>
  <Smaller @decrease="decreaseFontSize"/>
  <ListTitle @select-title="setTitle"/>
  <ListSize @select-size="setFontSize"/>
</template>
