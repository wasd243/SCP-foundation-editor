<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import VueMoveable from "vue3-moveable";
import { getEditor } from "../../../stores/editor.ts";
import { selectedImageBlockElement } from "../../../stores/editor/extensions/ImageE.ts";

const imageAlignmentClasses = ["alignleft", "alignright", "aligncenter"];
const imageFloatPositionClasses = ["floatleft", "floatright"];
const imagePositionClasses = [...imageAlignmentClasses, ...imageFloatPositionClasses];
const imagePositionGuideVisible = ref(false);
const imagePositionPreview = ref<"left" | "center" | "right" | null>(null);
const imagePositionDragHandle = ref<HTMLElement | null>(null);
const imagePositionDragHandleStyle = ref<Record<string, string>>({});
const selectedImageResizable = computed(() =>
    selectedImageBlockElement.value?.getAttribute("data-editor-no-resize") !== "true"
);
const selectedImageDraggable = computed(() =>
    Boolean(
        selectedImageBlockElement.value?.classList.contains("floatleft") ||
        selectedImageBlockElement.value?.classList.contains("floatright") ||
        selectedImageBlockElement.value?.classList.contains("alignleft") ||
        selectedImageBlockElement.value?.classList.contains("alignright") ||
        selectedImageBlockElement.value?.classList.contains("aligncenter")
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

function findImageContainerParent(element: HTMLElement) {
  let parent: HTMLElement | null = element.parentElement;
  let imageContainer: HTMLElement | null = null;

  while (parent) {
    if (parent.tagName.toLowerCase() === "div" && parent.classList.contains("image-container")) {
      imageContainer = parent;
    }

    parent = parent.parentElement;
  }

  return imageContainer;
}

function getImageContainerTarget(element: HTMLElement) {
  const parentImageContainer = findImageContainerParent(element);

  if (parentImageContainer) {
    return parentImageContainer;
  }

  if (element.tagName.toLowerCase() === "div" && element.classList.contains("image-container")) {
    return element;
  }

  return null;
}

function findNodePositionByElement(element: HTMLElement) {
  const editorInstance = getEditor();

  if (!editorInstance) {
    return null;
  }

  let position: number | null = null;

  editorInstance.state.doc.descendants((_node, pos) => {
    if (editorInstance.view.nodeDOM(pos) === element) {
      position = pos;
      return false;
    }

    return true;
  });

  return position;
}

function setSizeStyle(styleText: unknown, width: string, height: string) {
  const element = document.createElement("div");

  element.style.cssText = typeof styleText === "string" ? styleText : "";
  element.style.width = width;
  element.style.height = height;

  return element.style.cssText;
}

function setPositionStyle(styleText: unknown, margin: string) {
  const element = document.createElement("div");

  element.style.cssText = typeof styleText === "string" ? styleText : "";
  element.style.margin = margin;

  return element.style.cssText;
}

function updateImageContainerNodeStyle(container: HTMLElement, width: string, height: string) {
  const editorInstance = getEditor();
  const position = findNodePositionByElement(container);

  if (!editorInstance || position === null) {
    return;
  }

  const node = editorInstance.state.doc.nodeAt(position);

  if (!node) {
    return;
  }

  const attrsName = node.attrs.htmlAttributes && typeof node.attrs.htmlAttributes === "object"
      ? "htmlAttributes"
      : node.attrs.wrapperAttributes && typeof node.attrs.wrapperAttributes === "object"
          ? "wrapperAttributes"
          : null;

  if (!attrsName) {
    return;
  }

  const sizeAttributes = node.attrs[attrsName] as Record<string, unknown>;

  editorInstance.view.dispatch(
      editorInstance.state.tr.setNodeMarkup(position, undefined, {
        ...node.attrs,
        [attrsName]: {
          ...sizeAttributes,
          style: setSizeStyle(sizeAttributes.style, width, height),
        },
      }, node.marks)
  );
}

function updateImageContainerPositionNodeAttrs(container: HTMLElement, position: "left" | "center" | "right") {
  const editorInstance = getEditor();
  const nodePosition = findNodePositionByElement(container);

  if (!editorInstance || nodePosition === null) {
    return;
  }

  const node = editorInstance.state.doc.nodeAt(nodePosition);

  if (!node) {
    return;
  }

  const attrsName = node.attrs.htmlAttributes && typeof node.attrs.htmlAttributes === "object"
      ? "htmlAttributes"
      : node.attrs.wrapperAttributes && typeof node.attrs.wrapperAttributes === "object"
          ? "wrapperAttributes"
          : null;

  if (!attrsName) {
    return;
  }

  const positionAttributes = node.attrs[attrsName] as Record<string, unknown>;
  const className = typeof positionAttributes.class === "string" ? positionAttributes.class : "";
  const nextClassName = className
      .split(/\s+/)
      .filter(Boolean)
      .filter(className => !imagePositionClasses.includes(className));
  const margin = position === "left"
      ? "0 1em 0.8em 0"
      : position === "right"
          ? "0 0 0.8em 1em"
          : "0 auto 0.8em auto";

  nextClassName.push(getImagePositionClass(container, position));

  editorInstance.view.dispatch(
      editorInstance.state.tr.setNodeMarkup(nodePosition, undefined, {
        ...node.attrs,
        [attrsName]: {
          ...positionAttributes,
          class: nextClassName.join(" "),
          style: setPositionStyle(positionAttributes.style, margin),
        },
      }, node.marks)
  );
}

function getImageDropPosition(container: HTMLElement): "left" | "center" | "right" {
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

function setImageContainerPosition(container: HTMLElement, position: "left" | "center" | "right") {
  imagePositionClasses.forEach(className => container.classList.remove(className));
  container.querySelectorAll("div.image-container").forEach(child => {
    imagePositionClasses.forEach(className => child.classList.remove(className));
    child.classList.remove("image-container");

    if (child instanceof HTMLElement) {
      child.style.transform = "";
      child.style.margin = "";
    }
  });

  container.classList.add(getImagePositionClass(container, position));
  container.style.transform = "";
  container.style.margin = position === "left"
      ? "0 1em 0.8em 0"
      : position === "right"
          ? "0 0 0.8em 1em"
          : "0 auto 0.8em auto";
}

function getImagePositionClass(container: HTMLElement, position: "left" | "center" | "right") {
  if (container.hasAttribute("data-editor-include")) {
    return position === "left" ? "alignleft" : position === "right" ? "alignright" : "aligncenter";
  }

  return position === "left" ? "floatleft" : position === "right" ? "floatright" : "aligncenter";
}

function syncImageContainerSize(container: HTMLElement, width: string, height: string) {
  const img = container.querySelector("img") as HTMLElement | null;

  container.style.width = width;
  container.style.height = height;

  if (!img) {
    return;
  }

  img.style.width = width;
  img.style.height = height;
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

    setImageContainerPosition(container, position);
    updateImageContainerPositionNodeAttrs(container, position);
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
    syncImageContainerSize(container, width, height);
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
    syncImageContainerSize(container, width, height);
    updateImageContainerNodeStyle(container, width, height);
    setEditorDomObserverEnabled(true);
    updateImagePositionDragHandle();
    return;
  }

  target.style.width = width;
  target.style.height = height;
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
