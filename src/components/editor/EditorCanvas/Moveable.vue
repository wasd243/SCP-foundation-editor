<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import VueMoveable from "vue3-moveable";
import { getEditor } from "../../../stores/editor.ts";
import {
  findTopImageContainer,
  imagePositionClasses,
  setImageContainerPositionDom,
  syncImageContainerSizeDom,
  updateImageElementSizeAttrs,
  updateImageContainerPositionAttrs,
  updateImageContainerSizeAttrs,
  type ImagePosition,
} from "../../../stores/editor/extensions/ImageAttrE.ts";
import { selectedImageBlockElement } from "../../../stores/editor/extensions/ImageE.ts";

const imagePositionGuideVisible = ref(false);
const imagePositionPreview = ref<"left" | "center" | "right" | null>(null);
const imagePositionDragHandle = ref<HTMLElement | null>(null);
const imagePositionDragHandleStyle = ref<Record<string, string>>({});
// no-resize was a temporary development flag; Moveable resize is always enabled for selected images.
const selectedImageResizable = computed(() => Boolean(selectedImageBlockElement.value));
const selectedImageDraggable = computed(() =>
    Boolean(
        selectedImageBlockElement.value?.classList.contains("floatleft") ||
        selectedImageBlockElement.value?.classList.contains("floatright") ||
        (
            selectedImageBlockElement.value?.hasAttribute("data-editor-include") &&
            (
                selectedImageBlockElement.value.classList.contains("alignleft") ||
                selectedImageBlockElement.value.classList.contains("alignright") ||
                selectedImageBlockElement.value.classList.contains("aligncenter")
            )
        )
    )
);

function updateImagePositionDragHandle() {
  const target = selectedImageBlockElement.value;

  if (!target || !selectedImageDraggable.value) {
    imagePositionDragHandleStyle.value = {};
    return;
  }

  const rect = target.getBoundingClientRect();

  imagePositionDragHandleStyle.value = {
    left: `${rect.left + rect.width / 2}px`,
    top: `${rect.top + rect.height / 2}px`,
  };
}

function getImageContainerTarget(element: HTMLElement) {
  return findTopImageContainer(element);
}

function getImageDropPosition(container: HTMLElement): ImagePosition {
  const editorRoot = getEditor()?.view.dom;
  const rootRect = editorRoot?.getBoundingClientRect();
  const rect = container.getBoundingClientRect();

  if (!rootRect) {
    return "left";
  }

  const relativeCenter = rect.left + rect.width / 2 - rootRect.left;
  const third = rootRect.width / 3;

  if (relativeCenter < third) {
    return "left";
  }

  if (relativeCenter > third * 2) {
    return "right";
  }

  return "center";
}

function setEditorDomObserverEnabled(enabled: boolean) {
  const editorInstance = getEditor();
  //@ts-ignore
  const domObserver = editorInstance?.view.domObserver as {
    start?: () => void;
    stop?: () => void;
  } | undefined;

  if (enabled) {
    domObserver?.start?.();
  } else {
    domObserver?.stop?.();
  }
}

function onImageResizeStart() {
  setEditorDomObserverEnabled(false);
}

function onImageDragStart() {
  setEditorDomObserverEnabled(false);
  updateImagePositionDragHandle();
  imagePositionGuideVisible.value = true;
}

function onImageDrag(e: any) {
  const target = e.target as HTMLElement;
  const container = getImageContainerTarget(target);

  if (!container || !selectedImageDraggable.value) {
    return;
  }

  imagePositionGuideVisible.value = true;
  container.style.transform = e.transform;
  imagePositionPreview.value = getImageDropPosition(container);
}

function onImageDragEnd(e: any) {
  const target = (e.lastEvent?.target ?? e.target) as HTMLElement | undefined;
  const container = target ? getImageContainerTarget(target) : null;

  if (container && selectedImageDraggable.value) {
    const position = getImageDropPosition(container);

    setImageContainerPositionDom(container, position);
    updateImageContainerPositionAttrs(container, position);
  }

  imagePositionGuideVisible.value = false;
  imagePositionPreview.value = null;
  setEditorDomObserverEnabled(true);
  updateImagePositionDragHandle();
}

function onImageResize(e: any) {
  const target = e.target as HTMLElement;
  const width = `${e.width}px`;
  const height = `${e.height}px`;
  const container = getImageContainerTarget(target);

  if (container) {
    syncImageContainerSizeDom(container, width, height);
    updateImagePositionDragHandle();
    return;
  }

  target.style.width = width;
  target.style.height = height;
  updateImagePositionDragHandle();
}

function onImageResizeEnd(e: any) {
  const width = `${Math.round(e.lastEvent?.width ?? e.target.offsetWidth)}px`;
  const height = `${Math.round(e.lastEvent?.height ?? e.target.offsetHeight)}px`;
  const target = e.target as HTMLElement;
  const container = getImageContainerTarget(target);

  if (container) {
    syncImageContainerSizeDom(container, width, height);
    updateImageContainerSizeAttrs(container, width, height);
    setEditorDomObserverEnabled(true);
    updateImagePositionDragHandle();
    return;
  }

  target.style.width = width;
  target.style.height = height;
  updateImageElementSizeAttrs(target, width, height);
  setEditorDomObserverEnabled(true);
  updateImagePositionDragHandle();
}

watch(selectedImageBlockElement, () => {
  nextTick(updateImagePositionDragHandle);
});

watch(selectedImageDraggable, () => {
  nextTick(updateImagePositionDragHandle);
});

onMounted(() => {
  window.addEventListener("resize", updateImagePositionDragHandle);
  window.addEventListener("scroll", updateImagePositionDragHandle, true);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateImagePositionDragHandle);
  window.removeEventListener("scroll", updateImagePositionDragHandle, true);
});
</script>

<template>
  <div
      v-if="imagePositionGuideVisible"
      class="image-position-guides"
  >
    <div
        class="image-position-guide image-position-guide-left"
        :class="{ active: imagePositionPreview === 'left' }"
    />
    <div
        class="image-position-guide image-position-guide-center"
        :class="{ active: imagePositionPreview === 'center' }"
    />
    <div
        class="image-position-guide image-position-guide-right"
        :class="{ active: imagePositionPreview === 'right' }"
    />
  </div>

  <div
      v-show="selectedImageDraggable"
      ref="imagePositionDragHandle"
      class="image-position-drag-handle"
      :style="imagePositionDragHandleStyle"
      title="Move image position"
  />

  <VueMoveable
      :target="selectedImageBlockElement || undefined"
      :resizable="selectedImageResizable"
      :draggable="selectedImageDraggable"
      :dragTarget="imagePositionDragHandle || undefined"
      :dragTargetSelf="false"
      :keepRatio="false"
      :renderDirections="['nw', 'ne', 'sw', 'se', 'n', 'w', 's', 'e']"
      @dragStart="onImageDragStart"
      @drag="onImageDrag"
      @dragEnd="onImageDragEnd"
      @resizeStart="onImageResizeStart"
      @resize="onImageResize"
      @resizeEnd="onImageResizeEnd"
  />
</template>

<style scoped>
.image-position-guides {
  position: fixed;
  top: calc(var(--topbar-height) + var(--ribbon-height) + 32px);
  bottom: 0;
  left: 0;
  right: 0;
  width: min(900px, calc(100vw - 96px));
  margin: 0 auto;
  z-index: 9999;
  pointer-events: none;
}

.image-position-guide {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  border-left: 2px dashed rgba(37, 99, 235, 0.8);
  opacity: 0.9;
}

.image-position-guide.active {
  border-left-color: var(--color-word-blue);
  opacity: 1;
}

.image-position-guide-left {
  left: 15%;
}

.image-position-guide-center {
  left: 50%;
}

.image-position-guide-right {
  left: 85%;
}

.image-position-drag-handle {
  position: fixed;
  z-index: 10000;
  width: 12px;
  height: 12px;
  box-sizing: border-box;
  border: 2px solid #ffffff;
  border-radius: 50%;
  background: var(--wikidot-red);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.28);
  cursor: grab;
  pointer-events: auto;
  transform: translate(-50%, -50%);
}

.image-position-drag-handle:active {
  cursor: grabbing;
}

</style>
