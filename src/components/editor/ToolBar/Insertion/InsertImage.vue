<script setup lang="ts">
import InsertImageIcon from "../../../../assets/icons/InsertImage.svg";
import { promptEditorImage } from "../../../../stores/btnToolBar/btnInsertion/btnInsertImage.ts";
</script>

<template>
    <button
        class="format-insertion-button image-button"
        type="button"
        @click="promptEditorImage"
    >
        <img :src="InsertImageIcon" alt="Insert Image" />
        <br />
        Image
    </button>
</template>
