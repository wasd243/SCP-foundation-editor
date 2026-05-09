<script setup lang="ts">
import { ref } from "vue";
import ColorPicker from "./Color/ColorPicker.vue";
import { setColorPickerEditorColor } from "../../../../stores/btnToolBar/btnFormats/btnColor/btnColorPicker.ts";

const opened = ref(false);

function togglePicker() {
  opened.value = !opened.value;
}

function setTextColor(color: string) {
  setColorPickerEditorColor(color);
}

function colorIdleInterface() {}

defineExpose({
  colorIdleInterface,
});
</script>

<template>
  <div class="color-button-wrapper">
    <button
        class="format-color-button"
        @click="togglePicker"
    >
      A
    </button>

    <ColorPicker v-if="opened" @change-color="setTextColor" />
  </div>
</template>
