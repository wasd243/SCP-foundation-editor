<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button sub-s"
        :class="{ active: activeFormats.subscript }"
        type="button"
        @click="emit('toggle')"
    >
        X₂
    </button>
</template>
