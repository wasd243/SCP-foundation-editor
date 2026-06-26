<script setup lang="ts">
import TopBar from "./components/editor/TopBar.vue";
import "./styles/global.css";
import EditorCanvas from "./components/editor/EditorCanvas.vue";
import InputWindow from "./components/editor/InputWindow.vue";
import UpdateBanner from "./components/editor/UpdateBanner.vue";
import UpdateDialog from "./components/editor/UpdateDialog.vue";
</script>

<template>
    <TopBar />
    <UpdateBanner />
    <EditorCanvas />
    <InputWindow />
    <UpdateDialog />
</template>

<style scoped></style>
