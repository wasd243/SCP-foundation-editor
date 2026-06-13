<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button bold" type="button" @click="emit('toggle')">
    <b>B</b>
  </button>
</template>
