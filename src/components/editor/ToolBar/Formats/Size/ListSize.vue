<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{
  selectSize: [size: number];
}>();

const isOpen = ref(false);
const fontSizes = [12, 14];
const selectedSize = ref(fontSizes[0]);

function toggleList() {
  isOpen.value = !isOpen.value;
}

function selectSize(size: number) {
  selectedSize.value = size;
  isOpen.value = false;
  emit("selectSize", size);
}
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
