<script setup lang="ts">
import Left from "./Align/Left.vue";
import Right from "./Align/Right.vue";
import Middle from "./Align/Middle.vue";
import { alignLeftEditor } from "../../../../stores/btnToolBar/btnFormats/btnAlign/btnLeft.ts";
import { alignMiddleEditor } from "../../../../stores/btnToolBar/btnFormats/btnAlign/btnMiddle.ts";
import { alignRightEditor } from "../../../../stores/btnToolBar/btnFormats/btnAlign/btnRight.ts";

function alignLeft() {
  alignLeftEditor();
}

function alignMiddle() {
  alignMiddleEditor();
}

function alignRight() {
  alignRightEditor();
}

function alignIdleInterface() {}

defineExpose({
  alignIdleInterface,
});
</script>

<template>
  <Left @align="alignLeft"/>
  <Right @align="alignRight"/>
  <Middle @align="alignMiddle"/>
</template>
