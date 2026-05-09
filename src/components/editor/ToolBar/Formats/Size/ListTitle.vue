<script setup lang="ts">
import { ref } from "vue";

const isOpen = ref(false);
const titles = ["正文", "标题 1", "标题 2"]; // Waiting for data, going to be replaced by API
const selectedTitle = ref(titles[0]);

function toggleList() {
  isOpen.value = !isOpen.value;
}

function selectTitle(title: string) {
  selectedTitle.value = title;
  isOpen.value = false;
}
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
