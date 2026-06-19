<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button underline"
        :class="{ active: activeFormats.underline }"
        type="button"
        @click="emit('toggle')"
    >
        U
    </button>
</template>
