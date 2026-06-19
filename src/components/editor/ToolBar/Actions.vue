<script setup lang="ts">
import Redo from "./Actions/Redo.vue";
import Undo from "./Actions/Undo.vue";
import Save from "./Actions/Save.vue";
import OpenFile from "./Actions/OpenFile.vue";
import AutoSave from "./Actions/AutoSave.vue";
</script>

<template>
    <Redo />
    <Undo />
    <Save />
    <OpenFile />
    <AutoSave />
</template>
