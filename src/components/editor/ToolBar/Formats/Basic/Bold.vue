<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button bold"
        :class="{ active: activeFormats.bold }"
        type="button"
        @click="emit('toggle')"
    >
        <b>B</b>
    </button>
</template>
