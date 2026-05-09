<script setup lang="ts">
const emit = defineEmits<{
  align: [];
}>();
</script>

<template>
  <button class="format-basic-button align-center" type="button" @click="emit('align')">≡</button>
</template>
