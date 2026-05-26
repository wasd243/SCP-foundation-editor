<script setup lang="ts">
import InsertImageBlock from "../../../../assets/icons/InsertImageBlock.svg";
</script>

<template>
  <button class="format-insertion-button image-block-button" type="button">
    <img :src="InsertImageBlock" alt="Insert Image Block"/>
    <br>
    Caption
  </button>
</template>
