<script setup lang="ts">
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button quote"
        :class="{ active: activeFormats.blockquote }"
        type="button"
        @click="emit('toggle')"
    >
        “”
    </button>
</template>
