<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { getEditor } from "../../../../../stores/editor.ts";

const emit = defineEmits<{
  selectTitle: [title: string];
}>();

const isOpen = ref(false);
// --- Waiting for data, going to be replaced by API ---
const titles = ["content", "+1", "++2", "+++3", "++++4", "+++++5", "++++++6"];
// --- Waiting for data, going to be replaced by API ---
const selectedTitle = ref(titles[0]);
let stopWatchingEditor: (() => void) | null = null;
let editorWatchTimer: number | null = null;

function renderCurrentTitle() {
  const editor = getEditor();

  if (!editor?.isActive("heading")) {
    selectedTitle.value = titles[0];
    return;
  }

  const level = editor.getAttributes("heading").level;
  selectedTitle.value = typeof level === "number" && titles[level] ? titles[level] : titles[0];
}

function watchEditorTitle() {
  const editor = getEditor();

  if (!editor) {
    return false;
  }

  renderCurrentTitle();
  editor.on("selectionUpdate", renderCurrentTitle);
  editor.on("transaction", renderCurrentTitle);

  stopWatchingEditor = () => {
    editor.off("selectionUpdate", renderCurrentTitle);
    editor.off("transaction", renderCurrentTitle);
  };

  return true;
}

function toggleList() {
  isOpen.value = !isOpen.value;
}

function selectTitle(title: string) {
  selectedTitle.value = title;
  isOpen.value = false;
  emit("selectTitle", title);
}

onMounted(() => {
  if (watchEditorTitle()) {
    return;
  }

  editorWatchTimer = window.setInterval(() => {
    if (!watchEditorTitle() || editorWatchTimer === null) {
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
  <div class="format-size-list format-title-list">
    <button
      class="format-size-button list title"
      type="button"
      :aria-expanded="isOpen"
      @click="toggleList"
    >
      <span>{{ selectedTitle }}</span>
      <span class="format-size-button-arrow">⌄</span>
    </button>

    <div v-if="isOpen" class="format-size-menu format-title-menu">
      <button
        v-for="title in titles"
        :key="title"
        class="format-size-menu-item format-title-menu-item"
        type="button"
        @click="selectTitle(title)"
      >
        {{ title }}
      </button>
    </div>
  </div>
</template>
