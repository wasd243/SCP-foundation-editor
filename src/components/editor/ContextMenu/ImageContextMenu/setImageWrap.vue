<script setup lang="ts">
defineEmits<{
  clickCommand: [];
}>();
</script>

<template>
  <button
      class="context-menu-item"
      @click="$emit('clickCommand')"
  >
    <span>Wrap image</span>
  </button>
</template>
