<script setup lang="ts">
import SmallerSize from "../../../../../assets/icons/SmallerSize.svg";

const emit = defineEmits<{
    decrease: [];
}>();
</script>

<template>
    <button
        class="format-size-button smaller"
        type="button"
        @click="emit('decrease')"
    >
        <img :src="SmallerSize" alt="SmallerSize" />
    </button>
</template>

<!--Rules for the image size because the icon is too small than the button-->
<style scoped>
.format-size-button.smaller img {
    min-width: 230%;
    min-height: 230%;
}
</style>
