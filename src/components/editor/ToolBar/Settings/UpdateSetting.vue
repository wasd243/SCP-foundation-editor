<script setup lang="ts">
import { computed, onMounted } from "vue";
import {
    status,
    currentVersion,
    newVersion,
    checkForUpdates,
    loadCurrentVersion,
    openUpdateDialog,
} from "../../../../stores/updater.ts";

onMounted(loadCurrentVersion);

const statusLabel = computed(() => {
    switch (status.value) {
        case "checking":
            return "Checking…";
        case "available":
            return `Update available — v${newVersion.value}`;
        case "downloading":
            return "Downloading…";
        case "downloaded":
            return "Ready to restart";
        case "upToDate":
            return "Up to date";
        case "error":
            return "Check failed";
        default:
            return "";
    }
});

const isError = computed(() => status.value === "error");
const isAvailable = computed(
    () => status.value === "available" || status.value === "downloaded",
);

function onAction() {
    if (isAvailable.value) {
        openUpdateDialog();
    } else {
        void checkForUpdates(false);
    }
}
</script>

<template>
    <section class="update-setting" aria-label="Update settings">
        <header class="update-setting__eyebrow">Updates</header>

        <p class="update-setting__version">
            Current version
            <span class="update-setting__tag">v{{ currentVersion || "—" }}</span>
        </p>

        <div class="update-setting__controls" role="group">
            <button
                class="saves-chip"
                type="button"
                :disabled="status === 'checking' || status === 'downloading'"
                @click="onAction"
            >
                {{ isAvailable ? "View update…" : "Check for updates" }}
            </button>
        </div>

        <p
            v-if="statusLabel"
            class="update-setting__status"
            :class="{ 'is-error': isError, 'is-live': isAvailable }"
        >
            {{ statusLabel }}
        </p>
    </section>
</template>

<style scoped>
.update-setting {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 12px 0 12px;
    font-family: var(--font-ui);
    color: var(--color-text-main);
    user-select: none;
}

.update-setting__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

.update-setting__version {
    margin: 0;
    font-size: 12px;
    color: #5f6b7a;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.update-setting__tag {
    font-family: ui-monospace, "Cascadia Code", "Consolas", monospace;
    font-size: 11px;
    color: var(--color-word-blue);
    background: var(--color-word-blue-light);
    border: 1px solid var(--color-border);
    border-radius: 2px;
    padding: 1px 5px;
}

.update-setting__controls {
    display: inline-flex;
    gap: 4px;
}

.saves-chip {
    padding: 3px 9px;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    color: var(--color-text-main);
    font-size: 12px;
    line-height: 1;
    cursor: pointer;
    transition:
        background 0.12s ease,
        border-color 0.12s ease,
        color 0.12s ease;
}

.saves-chip:hover {
    background: var(--button-hover);
}

.saves-chip:disabled {
    opacity: 0.55;
    cursor: default;
}

.saves-chip:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}

.update-setting__status {
    margin: 0;
    font-size: 12px;
    color: #5f6b7a;
}

.update-setting__status.is-live {
    color: var(--color-autosave-live);
    font-weight: 600;
}

.update-setting__status.is-error {
    color: var(--wikidot-red);
}
</style>
