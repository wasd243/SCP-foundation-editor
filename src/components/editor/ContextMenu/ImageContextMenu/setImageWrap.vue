<script setup lang="ts">
import WarpImage from "../../../../assets/icons/WrapImage.svg";

defineEmits<{
    clickCommand: [];
}>();
</script>

<template>
    <button class="context-menu-item" @click="$emit('clickCommand')">
        <img :src="WarpImage" alt="Wrap image" />
        <span>Wrap image</span>
    </button>
</template>

<style scoped>
.context-menu-item img {
    max-width: 24px;
    max-height: 24px;
}
</style>
