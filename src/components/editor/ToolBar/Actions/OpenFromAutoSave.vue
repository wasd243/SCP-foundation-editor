<script setup lang="ts">
import Open2 from "../../../../assets/icons/Open2.svg";
import { OpenFromAutoSave } from "../../../../stores/btnToolBar/btnActions/btnOpenFromAutoSave.ts";
</script>

<template>
    <button
        class="actions-button open-auto-save"
        type="button"
        title="Open the latest auto-saved file (saves/autosave.ftml)"
        @click="OpenFromAutoSave"
    >
        <img :src="Open2" alt="Open auto-save" />
        Read From Auto Save
    </button>
</template>
