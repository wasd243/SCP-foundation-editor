<script setup lang="ts">
const emit = defineEmits<{
  insert: [];
}>();
</script>

<template>
  <button class="format-basic-button collapsible" type="button" @click="emit('insert')">▸▾</button>
</template>
