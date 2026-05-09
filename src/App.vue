<script setup lang="ts">
import TopBar from "./components/editor/TopBar.vue";
import "./styles/global.css";
import EditorCanvas from "./components/editor/EditorCanvas.vue";
import ContextMenu from "./components/editor/ContextMenu.vue";
</script>

<template>
  <TopBar/>
  <ContextMenu/>
  <EditorCanvas/>
</template>

<style scoped>

</style>