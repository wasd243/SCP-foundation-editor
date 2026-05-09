<script setup lang="ts">
function copyText() {
  document.execCommand("copy");
}
</script>

<template>
  <button
      class="context-menu-item"
      @click="copyText"
  >
    <span>Copy</span>
    <span class="context-menu-shortcut">Ctrl+C</span>
  </button>
</template>
