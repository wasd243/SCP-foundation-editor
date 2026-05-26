<script setup lang="ts">
import InsertImageBlock from "../../../../assets/icons/InsertImageBlock.svg";
import { promptEditorImageBlock } from "../../../../stores/btnToolBar/btnInsertion/btnInsertImageBlock.ts";
</script>

<template>
  <button class="format-insertion-button image-block-button" type="button" @click="promptEditorImageBlock">
    <img :src="InsertImageBlock" alt="Insert Image Block"/>
    <br>
    Caption
  </button>
</template>
