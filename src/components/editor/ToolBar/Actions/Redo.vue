<script setup lang="ts">
import { redoEditor } from "../../../../stores/btnToolBar/btnActions/btnRedo.ts";
import Redo from "../../../../assets/icons/Redo.svg";
</script>

<template>
    <button class="actions-button redo" type="button" @click="redoEditor">
        <img :src="Redo" alt="Redo" />
    </button>
</template>

<style scoped>
img {
    filter: invert(1);
}
</style>
