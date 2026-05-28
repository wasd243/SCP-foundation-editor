<script setup lang="ts">
import InlineImage from "../../../../assets/icons/InlineImage.svg";

defineEmits<{
  clickCommand: [];
}>();
</script>

<template>
  <button
      class="context-menu-item"
      @click="$emit('clickCommand')"
  >
    <img :src="InlineImage" alt="Inline image">
    <span>Inline image</span>
  </button>
</template>
