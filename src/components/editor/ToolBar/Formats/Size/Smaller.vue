<script setup lang="ts">
const emit = defineEmits<{
  decrease: [];
}>();
</script>

<template>
  <button class="format-size-button smaller" type="button" @click="emit('decrease')">A˅</button>
</template>
