<script setup lang="ts">
import { invoke } from "@tauri-apps/api/core";

async function openCodeView() {
  try {
    await invoke("open_code_view_window");
  } catch (error) {
    console.error(error);
  }
}
</script>

<template>
  <button
      class="code-view"
      type="button"
      @click="openCodeView"
  >
    &lt;/&gt;
  </button>
</template>
