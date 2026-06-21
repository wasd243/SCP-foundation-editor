<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button italic"
        :class="{ active: activeFormats.italic }"
        type="button"
        @click="emit('toggle')"
    >
        <i>I</i>
    </button>
</template>
