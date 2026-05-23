<script setup lang="ts">
import URLink from "./URL/URLink.vue";
import URLPreview from "./URL/URLPreview.vue";
import URLSite from "./URL/URLSite.vue";
import { insertURLinkEditor } from "../../../../stores/btnToolBar/btnFormats/btnURL/btnURLink.ts";
import { insertURLSiteEditor } from "../../../../stores/btnToolBar/btnFormats/btnURL/btnURLSite.ts";

function insertLink() {
  insertURLinkEditor();
}

function insertSiteLink() {
  insertURLSiteEditor();
}

function urlIdleInterface() {}

defineExpose({
  urlIdleInterface,
});
</script>

<template>
  <URLink @insert="insertLink"/>
  <URLSite @insert="insertSiteLink"/>
  <URLPreview/>
</template>
