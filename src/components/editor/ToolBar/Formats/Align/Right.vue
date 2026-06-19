<script setup lang="ts">
import AlignRight from "../../../../../assets/icons/AlignRight.svg";
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    align: [];
}>();
</script>

<template>
    <button
        class="format-basic-button align-right"
        :class="{ active: activeFormats.alignRight }"
        type="button"
        @click="emit('align')"
    >
        <img :src="AlignRight" alt="AlignRight" />
    </button>
</template>
