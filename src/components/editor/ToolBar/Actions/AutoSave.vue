<script setup lang="ts">
import { computed, ref, watch } from "vue";
import {
    autoSaveEnabled,
    autoSaveError,
    autoSaveIntervalSeconds,
    autoSaveLastSavedAt,
    autoSavePulse,
    toggleAutoSave,
} from "../../../../stores/btnToolBar/btnActions/btnAutoSave.ts";

// Bump a key on every successful save so the heartbeat ring restarts its
// animation (re-keying the element re-mounts it, replaying the CSS animation).
const beat = ref(0);
watch(autoSavePulse, () => {
    beat.value++;
});

function formatInterval(seconds: number): string {
    return seconds % 60 === 0 ? `${seconds / 60} min` : `${seconds}s`;
}

const statusTitle = computed(() => {
    if (autoSaveError.value) {
        return `Auto-save error — ${autoSaveError.value}`;
    }
    if (!autoSaveEnabled.value) {
        return "Auto-save is off — click to start saving to saves\\";
    }

    const every = formatInterval(autoSaveIntervalSeconds.value);
    if (autoSaveLastSavedAt.value === null) {
        return `Auto-saving every ${every} — waiting for first save`;
    }
    const at = new Date(autoSaveLastSavedAt.value).toLocaleTimeString();
    return `Auto-saving every ${every} — last saved ${at}`;
});
</script>

<template>
    <button
        class="actions-button auto-save"
        :class="{ 'is-on': autoSaveEnabled, 'has-error': autoSaveError }"
        type="button"
        role="switch"
        :aria-checked="autoSaveEnabled"
        :title="statusTitle"
        @click="toggleAutoSave"
    >
        <span class="auto-save__lamp" aria-hidden="true">
            <span class="auto-save__dot"></span>
            <span
                v-if="autoSaveEnabled && !autoSaveError"
                :key="beat"
                class="auto-save__ring"
            ></span>
        </span>
        <span class="auto-save__label">Auto-save</span>
    </button>
</template>
