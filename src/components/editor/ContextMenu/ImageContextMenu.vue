<script setup lang="ts">
import SetImageInline from "./ImageContextMenu/setImageInline.vue";
import SetImageWrap from "./ImageContextMenu/setImageWrap.vue";
import {
  findTopImageContainer,
  setPlainImageFlowDom,
  updatePlainImageFlowAttrs,
} from "../../../stores/editor/extensions/ImageAttrE.ts";
import { selectedImageBlockElement } from "../../../stores/editor/extensions/ImageE.ts";

function getSelectedImageContainer() {
  const target = selectedImageBlockElement.value;

  if (!target) {
    return null;
  }

  const container = findTopImageContainer(target);

  if (!(container instanceof HTMLElement) || container.hasAttribute("data-editor-include")) {
    return null;
  }

  return container;
}

function setImageInline() {
  const container = getSelectedImageContainer();

  if (!container) {
    return;
  }

  setPlainImageFlowDom(container, "inline");
  updatePlainImageFlowAttrs(container, "inline");
}

function setImageWrap() {
  const container = getSelectedImageContainer();

  if (!container) {
    return;
  }

  setPlainImageFlowDom(container, "wrap");
  updatePlainImageFlowAttrs(container, "wrap");
}
</script>

<template>
  <div class="context-menu-section">
    <SetImageInline @click-command="setImageInline"/>
    <SetImageWrap @click-command="setImageWrap"/>
  </div>
</template>
