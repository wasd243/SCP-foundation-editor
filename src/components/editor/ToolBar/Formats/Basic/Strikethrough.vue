<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button strikethrough" type="button" @click="emit('toggle')">S</button>
</template>
