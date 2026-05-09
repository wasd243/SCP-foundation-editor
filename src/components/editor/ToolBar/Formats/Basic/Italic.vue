<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button italic" type="button" @click="emit('toggle')">I</button>
</template>
