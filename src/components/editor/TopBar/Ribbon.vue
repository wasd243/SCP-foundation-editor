<script setup lang="ts">
import HomePage from "./Ribbon/HomePage.vue";
import InsertPage from "./Ribbon/InsertPage.vue";
import SettingsPage from "./Ribbon/SettingsPage.vue";

type Tab = "home" | "insert" | "settings";

defineProps<{ activeTab: Tab }>();
</script>

<template>
  <section class="ribbon-page" aria-label="Ribbon commands">
    <HomePage v-if="activeTab === 'home'" />
    <InsertPage v-else-if="activeTab === 'insert'" />
    <SettingsPage v-else />
  </section>
</template>
