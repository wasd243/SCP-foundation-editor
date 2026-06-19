<script setup lang="ts">
import AlignLeft from "../../../../../assets/icons/AlignLeft.svg";
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    align: [];
}>();
</script>

<template>
    <button
        class="format-basic-button align-left"
        :class="{ active: activeFormats.alignLeft }"
        type="button"
        @click="emit('align')"
    >
        <img :src="AlignLeft" alt="AlignLeft" />
    </button>
</template>

<style scoped>
/* To prevent image size larger than the button */
img {
    max-width: 100%;
    max-height: 100%;
}
</style>
