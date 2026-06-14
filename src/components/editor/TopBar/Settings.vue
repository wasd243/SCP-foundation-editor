<script setup lang="ts">
defineProps<{ active: boolean }>();
defineEmits<{ select: [] }>();
</script>

<template>
    <button
        class="top-tab"
        :class="{ active }"
        type="button"
        :aria-current="active ? 'page' : undefined"
        @click="$emit('select')"
    >
        Settings
    </button>
</template>
