<script setup lang="ts">
import AlignCenter from "../../../../../assets/icons/AlignCenter.svg";

const emit = defineEmits<{
  align: [];
}>();
</script>

<template>
  <button class="format-basic-button align-center" type="button" @click="emit('align')">
    <img :src="AlignCenter" alt="AlignCenter" />
  </button>
</template>
