<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button strikethrough"
        :class="{ active: activeFormats.strike }"
        type="button"
        @click="emit('toggle')"
    >
        S
    </button>
</template>
