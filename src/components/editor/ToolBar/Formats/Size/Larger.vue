<script setup lang="ts">
import LargerSize from "../../../../../assets/icons/LargerSize.svg";

const emit = defineEmits<{
    increase: [];
}>();
</script>

<template>
    <button
        class="format-size-button larger"
        type="button"
        @click="emit('increase')"
    >
        <img :src="LargerSize" alt="LargerSize" />
    </button>
</template>

<!--Rules for the image size because the icon is too small than the button-->
<style scoped>
.format-size-button.larger img {
    min-width: 230%;
    min-height: 230%;
}
</style>
