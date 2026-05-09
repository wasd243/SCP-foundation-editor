<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button list-ul" type="button" @click="emit('toggle')">#</button>
</template>
