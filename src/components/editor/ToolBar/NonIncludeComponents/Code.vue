<script setup lang="ts">
import { insertEditorCode } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnCode.ts";
</script>

<template>
  <button class="component-card" type="button" @click="insertEditorCode">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path
          d="M7.5 6L4 10L7.5 14"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linecap="round"
          stroke-linejoin="round"
      />
      <path
          d="M12.5 6L16 10L12.5 14"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linecap="round"
          stroke-linejoin="round"
      />
      <path
          d="M11 5L9 15"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linecap="round"
      />
    </svg>
    Code
  </button>
</template>
