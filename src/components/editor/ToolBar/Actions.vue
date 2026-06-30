<script setup lang="ts">
import Redo from "./Actions/Redo.vue";
import Undo from "./Actions/Undo.vue";
import Save from "./Actions/Save.vue";
import OpenFile from "./Actions/OpenFile.vue";
import AutoSave from "./Actions/AutoSave.vue";
import OpenFromAutoSave from "./Actions/OpenFromAutoSave.vue";
import Settings from "./Actions/Settings.vue";
</script>

<template>
    <div class="actions-bar">
        <OpenFromAutoSave />
        <OpenFile />
        <Save />
        <span class="actions-divider" aria-hidden="true"></span>
        <AutoSave />
        <span class="actions-divider" aria-hidden="true"></span>
        <Undo />
        <Redo />
        <Settings />
    </div>
</template>
