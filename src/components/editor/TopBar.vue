<template>
  <nav class="top-bar" aria-label="Editor sections">
    <button class="top-tab active">Home</button>
    <button class="top-tab">Insert</button>
    <button class="top-tab">Settings</button>
  </nav>
</template>

<style scoped>
.top-bar {
  height: 44px;
  display: flex;
  align-items: end;
  gap: 4px;
  padding: 0 12px;
  background: #f3f6fb;
  border-bottom: 1px solid #c8d3e6;
}

.top-tab {
  height: 36px;
  padding: 0 18px;
  border: 0;
  border-radius: 6px 6px 0 0;
  background: transparent;
  color: #1f3b63;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.top-tab:hover {
  background: #e5eefc;
}

.top-tab.active {
  background: #ffffff;
  color: #0f4c9c;
  border: 1px solid #c8d3e6;
  border-bottom-color: #ffffff;
}
</style>