<!--
This is the top bar of the editor, including the tabs and the ribbon,all of which are controlled by the Ribbon component.
All controllers are in the Ribbon pages.
-->

<script setup lang="ts">
import { ref } from "vue";

import TopBarHome from "./TopBar/Home.vue";
import Insert from "./TopBar/Insert.vue";
import Ribbon from "./TopBar/Ribbon.vue";
import Settings from "./TopBar/Settings.vue";
import Actions from "./ToolBar/Actions.vue";

type Tab = "home" | "insert" | "settings";

const activeTab = ref<Tab>("home");
</script>

<template>
  <header class="editor-top">
    <nav class="top-bar" aria-label="Editor sections">
      <TopBarHome :active="activeTab === 'home'" @select="activeTab = 'home'" />
      <Insert :active="activeTab === 'insert'" @select="activeTab = 'insert'" />
      <Settings :active="activeTab === 'settings'" @select="activeTab = 'settings'" />
    </nav>

    <!--Actions bar, contains undo, redo, save, open, etc.-->
    <Actions/>
    <Ribbon :active-tab="activeTab" />
  </header>
</template>

<style scoped>
.editor-top {
  width: 100%;
  position: relative;
  z-index: 20;
  flex: 0 0 auto;
}

.top-bar {
  height: var(--topbar-height);
  display: flex;
  align-items: end;
  gap: 4px;
  padding: 0 12px;

  background: var(--color-word-blue);
  border-bottom: 1px solid var(--color-word-blue-dark);
  font-family: var(--font-ui),sans-serif;
}

.top-tab {
  height: var(--tab-height);
  padding: 0 18px;

  border: 0;

  background: transparent;
  color: var(--color-text-on-blue);

  font-weight: 600;
  cursor: pointer;
}

.top-tab:hover {
  background: rgba(255, 255, 255, 0.16);
}

.top-tab.active {
  background: var(--color-bg-surface);
  color: var(--color-word-blue);
}
</style>
