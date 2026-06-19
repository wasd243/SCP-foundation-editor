<script setup lang="ts">
import AlignCenter from "../../../../../assets/icons/AlignCenter.svg";
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    align: [];
}>();
</script>

<template>
    <button
        class="format-basic-button align-center"
        :class="{ active: activeFormats.alignCenter }"
        type="button"
        @click="emit('align')"
    >
        <img :src="AlignCenter" alt="AlignCenter" />
    </button>
</template>
