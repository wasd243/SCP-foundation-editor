<script setup lang="ts">
import URLink from "./URL/URLink.vue";
import URLPreview from "./URL/URLPreview.vue";
import { insertURLinkEditor } from "../../../../stores/btnToolBar/btnFormats/btnURL/btnURLink.ts";

function insertLink() {
  insertURLinkEditor();
}

function urlIdleInterface() {}

defineExpose({
  urlIdleInterface,
});
</script>

<template>
  <URLink @insert="insertLink"/>
  <URLPreview/>
</template>
