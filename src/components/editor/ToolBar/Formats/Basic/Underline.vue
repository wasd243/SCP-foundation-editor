<script setup lang="ts">
const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button underline"
        type="button"
        @click="emit('toggle')"
    >
        U
    </button>
</template>
