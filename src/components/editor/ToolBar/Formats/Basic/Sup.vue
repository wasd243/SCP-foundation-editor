<script setup lang="ts">
const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button sup-s"
        type="button"
        @click="emit('toggle')"
    >
        X²
    </button>
</template>
