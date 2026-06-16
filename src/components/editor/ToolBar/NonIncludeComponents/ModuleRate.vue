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

/**
 * Toggle MODULE_RATE between TRUE/FALSE and write it back to the temp file.
 * The existing ALIGNMENTS line is preserved.
 *
 * Note: the parser rewrites this same file on every `parse_wikidot` call, so a
 * later parse can override this manual toggle. That is expected until the
 * exporter wires the module-rate status back into the source text.
 */
async function toggleModuleRateStatus() {
    isActived.value = !isActived.value;
    const status = isActived.value ? "MODULE_RATE=TRUE" : "MODULE_RATE=FALSE";

    let alignment = "ALIGNMENTS=NONE";
    try {
        const current = await invoke<string>("read_module_rate_temp");
        alignment = /ALIGNMENTS=\w+/i.exec(current)?.[0] ?? alignment;
    } catch {
        // No temp file yet; fall back to the default alignment.
    }

    try {
        await invoke("rewrite_module_rate_temp", { status, alignment });
        // Notify the canvas so the rate box shows/hides to match the toggle.
        window.dispatchEvent(new CustomEvent("module-rate-status-changed"));
    } catch (error) {
        console.warn("Failed to rewrite module-rate status.", error);
    }
}

onMounted(() => {
    // Restore the status from temp on mount: switching ribbon pages unmounts
    // and remounts this component, which would otherwise reset the state.
    refreshModuleRateStatus();

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
    <button
        class="component-card module-rate"
        :class="{ actived: isActived }"
        @click="toggleModuleRateStatus"
    >
        ModuleRate
    </button>
</template>
