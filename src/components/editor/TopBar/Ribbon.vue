<script setup lang="ts">
import HomePage from "./Ribbon/HomePage.vue";
import InsertPage from "./Ribbon/InsertPage.vue";

type Tab = "home" | "insert";

defineProps<{ activeTab: Tab }>();
</script>

<template>
    <section class="ribbon-page" aria-label="Ribbon commands">
        <HomePage v-if="activeTab === 'home'" />
        <InsertPage v-else />
    </section>
</template>
