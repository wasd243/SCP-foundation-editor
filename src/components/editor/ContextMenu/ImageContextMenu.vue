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

  let current: Element | null = target;
  let container: Element | null = null;

  while (current) {
    if (current.classList.contains("image-container")) {
      container = current;
    }

    current = current.parentElement;
  }

  if (!(container instanceof HTMLElement) || container.hasAttribute("data-editor-include")) {
    return null;
  }

  return container;
}

function clearNestedImageContainer(container: HTMLElement) {
  container.querySelectorAll("div.image-container").forEach(child => {
    imagePositionClasses.forEach(className => child.classList.remove(className));
    child.classList.remove("image-container");

    if (child instanceof HTMLElement) {
      child.style.transform = "";
      child.style.margin = "";
    }
  });
}

function setImageInline() {
  const container = getSelectedImageContainer();

  if (!container) {
    return;
  }

  imagePositionClasses.forEach(className => container.classList.remove(className));
  clearNestedImageContainer(container);
  container.removeAttribute("data-editor-no-resize");
}

function setImageWrap() {
  const container = getSelectedImageContainer();

  if (!container) {
    return;
  }

  imagePositionClasses.forEach(className => container.classList.remove(className));
  clearNestedImageContainer(container);
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
