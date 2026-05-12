<script setup lang="ts">
const emit = defineEmits<{
  clickCommand: [];
}>();
</script>

<template>
  <button class="context-menu-item table-context-menu-item" type="button" @click="emit('clickCommand')">
    <span>Add Tab</span>
  </button>
</template>
