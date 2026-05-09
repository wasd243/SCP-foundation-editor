<script setup lang="ts">
import { ref } from "vue";
import ColorPicker from "./Color/ColorPicker.vue";

const opened = ref(false);

function togglePicker() {
  opened.value = !opened.value;
}
</script>

<template>
  <div class="color-button-wrapper">
    <button
        class="format-color-button"
        @click="togglePicker"
    >
      A
    </button>

    <ColorPicker v-if="opened" />
  </div>
</template>