<script setup lang="ts">
import TopBarHome from "./TopBar/Home.vue";
import Insert from "./TopBar/Insert.vue";
import Settings from "./TopBar/Settings.vue";
</script>

<template>
  <nav class="top-bar" aria-label="Editor sections">
    <TopBarHome/>
    <Insert/>
    <Settings/>
  </nav>
</template>

<style scoped>
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
