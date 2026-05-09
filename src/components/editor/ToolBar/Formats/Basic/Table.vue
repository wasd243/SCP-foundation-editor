<script setup lang="ts">
const emit = defineEmits<{
  insert: [];
}>();
</script>

<template>
  <button class="format-basic-button table" type="button" @click="emit('insert')">▦</button>
</template>
