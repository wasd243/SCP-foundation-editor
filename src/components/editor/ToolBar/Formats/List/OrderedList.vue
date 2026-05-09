<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button list-ol" type="button" @click="emit('toggle')">1.</button>
</template>
