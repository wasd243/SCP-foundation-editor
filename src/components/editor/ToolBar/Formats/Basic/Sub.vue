<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button sub-s" type="button" @click="emit('toggle')">X₂</button>
</template>
