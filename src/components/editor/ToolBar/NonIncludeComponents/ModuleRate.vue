<script setup lang="ts">
import { invoke } from "@tauri-apps/api/core";
import { onMounted, onUnmounted, ref } from "vue";

const isActived = ref(false);

/**
 * Refresh the button state from the parser's module-rate temp file.
 * The file is rewritten by the parser on every `parse_wikidot` call.
 */
async function refreshModuleRateStatus() {
    try {
        const status = await invoke<string>("read_module_rate_temp");
        isActived.value = /MODULE_RATE=TRUE/i.test(status);
    } catch (error) {
        console.warn("Failed to read module-rate status.", error);
    }
}

onMounted(() => {
    window.addEventListener(
        "module-rate-status-changed",
        refreshModuleRateStatus,
    );
});

onUnmounted(() => {
    window.removeEventListener(
        "module-rate-status-changed",
        refreshModuleRateStatus,
    );
});
</script>

<template>
    <button class="component-card module-rate" :class="{ actived: isActived }">
        ModuleRate
    </button>
</template>
