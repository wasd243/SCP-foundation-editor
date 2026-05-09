<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { getEditor } from "../../../../../stores/editor.ts";

const emit = defineEmits<{
  selectSize: [size: number];
}>();

const defaultFontSize = 16;
const isOpen = ref(false);
const fontSizes = [12, 14];
const selectedSize = ref(defaultFontSize);
let stopWatchingEditor: (() => void) | null = null;
let editorWatchTimer: number | null = null;

function parseFontSize(size: unknown) {
  if (typeof size !== "string") {
    return defaultFontSize;
  }

  const parsedSize = Number.parseInt(size, 10);
  return Number.isFinite(parsedSize) ? parsedSize : defaultFontSize;
}

function renderCurrentFontSize() {
  selectedSize.value = parseFontSize(getEditor()?.getAttributes("fontSize").size);
}

function watchEditorFontSize() {
  const editor = getEditor();

  if (!editor) {
    return false;
  }

  renderCurrentFontSize();
  editor.on("selectionUpdate", renderCurrentFontSize);
  editor.on("transaction", renderCurrentFontSize);

  stopWatchingEditor = () => {
    editor.off("selectionUpdate", renderCurrentFontSize);
    editor.off("transaction", renderCurrentFontSize);
  };

  return true;
}

function toggleList() {
  isOpen.value = !isOpen.value;
}

function selectSize(size: number) {
  selectedSize.value = size;
  isOpen.value = false;
  emit("selectSize", size);
}

onMounted(() => {
  if (watchEditorFontSize()) {
    return;
  }

  editorWatchTimer = window.setInterval(() => {
    if (!watchEditorFontSize() || editorWatchTimer === null) {
      return;
    }

    window.clearInterval(editorWatchTimer);
    editorWatchTimer = null;
  }, 100);
});

onUnmounted(() => {
  stopWatchingEditor?.();

  if (editorWatchTimer !== null) {
    window.clearInterval(editorWatchTimer);
  }
});
</script>

<template>
  <div class="format-size-list">
    <button
      class="format-size-button list"
      type="button"
      :aria-expanded="isOpen"
      @click="toggleList"
    >
      <span>{{ selectedSize }}</span>
      <span class="format-size-button-arrow">⌄</span>
    </button>

    <div v-if="isOpen" class="format-size-menu">
      <button
        v-for="size in fontSizes"
        :key="size"
        class="format-size-menu-item"
        type="button"
        @click="selectSize(size)"
      >
        {{ size }}
      </button>
    </div>
  </div>
</template>
