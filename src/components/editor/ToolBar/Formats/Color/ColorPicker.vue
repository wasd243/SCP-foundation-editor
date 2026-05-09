<script setup lang="ts">
import { ref, watch } from "vue";
import { ColorPicker } from "vue3-colorpicker";

const color = ref("#ff0000");

watch(color, (newColor) => {
  console.log(newColor);
});
</script>

<template>
  <div class="color-picker-wrapper">
    <ColorPicker
        v-model:pureColor="color"
        :isWidget="true"
    />
  </div>
</template>