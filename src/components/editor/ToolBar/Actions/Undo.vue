<script setup lang="ts">
import { undoEditor } from "../../../../stores/btnToolBar/btnActions/btnUndo.ts";
import Undo from "../../../../assets/icons/Undo.svg";
</script>

<template>
    <button class="actions-button undo" type="button" @click="undoEditor">
        <img :src="Undo" alt="Undo" />
    </button>
</template>

<style scoped>
img {
    filter: invert(1);
}
</style>
