<script setup lang="ts">
import UnorderedList from "../../../../../assets/icons/UnorderedList.svg";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button list-ul"
        type="button"
        @click="emit('toggle')"
    >
        <img :src="UnorderedList" alt="UnorderedList" />
    </button>
</template>
