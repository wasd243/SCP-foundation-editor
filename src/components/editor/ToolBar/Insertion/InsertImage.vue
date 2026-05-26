<script setup lang="ts">
import InsertImageIcon from "../../../../assets/icons/InsertImage.svg";
</script>

<template>
  <button class="format-insertion-button image-button" type="button">
    <img :src="InsertImageIcon" alt="Insert Image"/>
    <br>
    Image
  </button>
</template>
