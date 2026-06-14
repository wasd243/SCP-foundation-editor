<script setup lang="ts">
import { ref, watch } from "vue";
import { ColorPicker } from "vue3-colorpicker";

const emit = defineEmits<{
    changeColor: [color: string];
}>();

const color = ref("#ff0000");

watch(color, (newColor) => {
    emit("changeColor", newColor);
});
</script>

<template>
    <div class="color-picker-wrapper">
        <ColorPicker v-model:pureColor="color" :isWidget="true" />
    </div>
</template>
