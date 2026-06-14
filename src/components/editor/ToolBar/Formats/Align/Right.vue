<script setup lang="ts">
import AlignRight from "../../../../../assets/icons/AlignRight.svg";

const emit = defineEmits<{
    align: [];
}>();
</script>

<template>
    <button
        class="format-basic-button align-right"
        type="button"
        @click="emit('align')"
    >
        <img :src="AlignRight" alt="AlignRight" />
    </button>
</template>
