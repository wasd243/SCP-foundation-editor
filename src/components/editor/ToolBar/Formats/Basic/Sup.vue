<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button sup-s"
        :class="{ active: activeFormats.superscript }"
        type="button"
        @click="emit('toggle')"
    >
        X²
    </button>
</template>
