<script setup lang="ts">
const emit = defineEmits<{
  align: [];
}>();
</script>

<template>
  <button class="format-basic-button align-left" type="button" @click="emit('align')">←</button>
</template>
