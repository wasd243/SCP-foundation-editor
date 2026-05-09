<script setup lang="ts">
const emit = defineEmits<{
  increase: [];
}>();
</script>

<template>
  <button class="format-size-button larger" type="button" @click="emit('increase')">A^</button>
</template>
