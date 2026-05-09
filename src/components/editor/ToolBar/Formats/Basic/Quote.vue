<script setup lang="ts">
const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button quote" type="button" @click="emit('toggle')">“”</button>
</template>
