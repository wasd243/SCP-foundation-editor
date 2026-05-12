<script setup lang="ts">
const emit = defineEmits<{
  clickCommand: [];
}>();
</script>

<template>
  <button class="context-menu-item table-context-menu-item danger" type="button" @click="emit('clickCommand')">
    <span>Delete TabView</span>
  </button>
</template>
