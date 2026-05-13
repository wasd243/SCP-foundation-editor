<script setup lang="ts">
import { insertEditorTabView } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnTabView.ts";
</script>

<template>
  <button class="component-card" type="button" @click="insertEditorTabView">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <rect
          x="3"
          y="6"
          width="14"
          height="11"
          rx="1"
          stroke="currentColor"
          stroke-width="1.4"
      />
      <path
          d="M4 6V4.5H8V6"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linejoin="round"
      />
      <path
          d="M8 6V4.5H12V6"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linejoin="round"
      />
      <path
          d="M12 6V4.5H16V6"
          stroke="currentColor"
          stroke-width="1.4"
          stroke-linejoin="round"
      />
      <line
          x1="4"
          y1="9"
          x2="16"
          y2="9"
          stroke="currentColor"
          stroke-width="1"
      />
    </svg>
    TabView
  </button>
</template>
