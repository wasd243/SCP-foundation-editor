<script setup lang="ts">
import SetImageInline from "./ImageContextMenu/setImageInline.vue";
import SetImageWrap from "./ImageContextMenu/setImageWrap.vue";
import { selectedImageBlockElement } from "../../../stores/editor/extensions/ImageE.ts";

const imagePositionClasses = ["alignleft", "alignright", "aligncenter", "floatleft", "floatright"];

function getSelectedImageContainer() {
  const target = selectedImageBlockElement.value;

  if (!target) {
    return null;
  }

  const container = target.classList.contains("image-container")
      ? target
      : target.closest(".image-container");

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

  imagePositionClasses.forEach(className => container.classList.remove(className));
  container.removeAttribute("data-editor-no-resize");
}

function setImageWrap() {
  const container = getSelectedImageContainer();

  if (!container) {
    return;
  }

  imagePositionClasses.forEach(className => container.classList.remove(className));
  container.classList.add("floatleft");
  container.removeAttribute("data-editor-no-resize");
}
</script>

<template>
  <div class="context-menu-section">
    <SetImageInline @click-command="setImageInline"/>
    <SetImageWrap @click-command="setImageWrap"/>
  </div>
</template>
