<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from "vue";
import {
    status,
    currentVersion,
    newVersion,
    releaseNotes,
    errorMessage,
    progress,
    dialogOpen,
    closeUpdateDialog,
    downloadAndInstallUpdate,
    restartApp,
    checkForUpdates,
} from "../../stores/updater.ts";

const percent = computed(() => {
    const { downloaded, total } = progress.value;
    if (!total) return 0;
    return Math.min(100, Math.round((downloaded / total) * 100));
});

const downloadedMb = computed(() =>
    (progress.value.downloaded / 1_048_576).toFixed(1),
);
const totalMb = computed(() =>
    progress.value.total ? (progress.value.total / 1_048_576).toFixed(1) : "—",
);

function onKey(e: KeyboardEvent) {
    if (e.key === "Escape") closeUpdateDialog();
}

watch(dialogOpen, (open) => {
    if (open) {
        window.addEventListener("keydown", onKey);
    } else {
        window.removeEventListener("keydown", onKey);
    }
});

onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>

<template>
    <Transition name="update-fade">
        <div
            v-if="dialogOpen"
            class="update-backdrop"
            @click.self="closeUpdateDialog"
        >
            <div
                class="update-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="update-modal-title"
            >
                <header class="update-modal__head">
                    <h2 id="update-modal-title" class="update-modal__title">
                        Software update
                    </h2>
                    <button
                        class="update-modal__close"
                        type="button"
                        aria-label="Close"
                        @click="closeUpdateDialog"
                    >
                        ✕
                    </button>
                </header>

                <div class="update-modal__versions">
                    <span class="ver">v{{ currentVersion || "—" }}</span>
                    <span class="arrow" aria-hidden="true">→</span>
                    <span class="ver ver--new">v{{ newVersion || "—" }}</span>
                </div>

                <section
                    v-if="releaseNotes"
                    class="update-modal__notes"
                    aria-label="Release notes"
                >
                    <pre>{{ releaseNotes }}</pre>
                </section>
                <p v-else class="update-modal__notes-empty">
                    No release notes were provided for this version.
                </p>

                <!-- Downloading: byte progress. -->
                <div
                    v-if="status === 'downloading'"
                    class="update-modal__progress"
                >
                    <div class="bar" role="progressbar" :aria-valuenow="percent">
                        <div class="bar__fill" :style="{ width: percent + '%' }"></div>
                    </div>
                    <p class="update-modal__progress-text">
                        {{ downloadedMb }} MB / {{ totalMb }} MB ({{ percent }}%)
                    </p>
                </div>

                <!-- Error. -->
                <p v-if="status === 'error'" class="update-modal__error">
                    {{ errorMessage }}
                </p>

                <footer class="update-modal__foot">
                    <template v-if="status === 'downloaded'">
                        <span class="update-modal__ok">Update installed.</span>
                        <button
                            class="btn btn--ghost"
                            type="button"
                            @click="closeUpdateDialog"
                        >
                            Later
                        </button>
                        <button
                            class="btn btn--primary"
                            type="button"
                            @click="restartApp"
                        >
                            Restart now
                        </button>
                    </template>

                    <template v-else-if="status === 'downloading'">
                        <button class="btn btn--primary" type="button" disabled>
                            Downloading…
                        </button>
                    </template>

                    <template v-else-if="status === 'error'">
                        <button
                            class="btn btn--ghost"
                            type="button"
                            @click="closeUpdateDialog"
                        >
                            Close
                        </button>
                        <button
                            class="btn btn--primary"
                            type="button"
                            @click="checkForUpdates(false)"
                        >
                            Try again
                        </button>
                    </template>

                    <template v-else>
                        <button
                            class="btn btn--ghost"
                            type="button"
                            @click="closeUpdateDialog"
                        >
                            Later
                        </button>
                        <button
                            class="btn btn--primary"
                            type="button"
                            @click="downloadAndInstallUpdate"
                        >
                            Install update
                        </button>
                    </template>
                </footer>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
.update-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.42);
    font-family: var(--font-ui);
}

.update-modal {
    width: min(480px, calc(100vw - 32px));
    max-height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
    background: var(--color-bg-surface);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28);
    color: var(--color-text-main);
}

.update-modal__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    background: var(--color-word-blue);
    border-radius: 4px 4px 0 0;
}

.update-modal__title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-on-blue);
}

.update-modal__close {
    border: 0;
    background: transparent;
    color: var(--color-text-on-blue);
    font-size: 14px;
    line-height: 1;
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 3px;
}

.update-modal__close:hover {
    background: rgba(255, 255, 255, 0.18);
}

.update-modal__versions {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px 6px;
    font-family: ui-monospace, "Cascadia Code", "Consolas", monospace;
    font-size: 18px;
    letter-spacing: 0.5px;
}

.update-modal__versions .ver {
    color: #5f6b7a;
}

.update-modal__versions .ver--new {
    color: var(--color-word-blue);
    font-weight: 700;
}

.update-modal__versions .arrow {
    color: var(--color-border);
    font-size: 16px;
}

.update-modal__notes {
    margin: 6px 16px;
    padding: 10px 12px;
    flex: 1 1 auto;
    overflow: auto;
    background: var(--color-bg-app);
    border: 1px solid var(--color-border);
    border-radius: 3px;
}

.update-modal__notes pre {
    margin: 0;
    font-family: var(--font-ui);
    font-size: 12.5px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
}

.update-modal__notes-empty {
    margin: 6px 16px;
    font-size: 12.5px;
    color: #5f6b7a;
}

.update-modal__progress {
    padding: 4px 16px 0;
}

.bar {
    height: 8px;
    border-radius: 999px;
    background: var(--color-word-blue-light);
    overflow: hidden;
}

.bar__fill {
    height: 100%;
    background: var(--color-word-blue);
    transition: width 0.15s ease;
}

.update-modal__progress-text {
    margin: 6px 0 0;
    font-size: 12px;
    color: #5f6b7a;
    font-variant-numeric: tabular-nums;
}

.update-modal__error {
    margin: 6px 16px 0;
    font-size: 12.5px;
    color: var(--wikidot-red);
    word-break: break-word;
}

.update-modal__foot {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    padding: 14px 16px;
}

.update-modal__ok {
    margin-right: auto;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--color-autosave-live);
}

.btn {
    font: inherit;
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 3px;
    cursor: pointer;
    transition:
        background 0.12s ease,
        border-color 0.12s ease;
}

.btn--ghost {
    border: 1px solid var(--color-border);
    background: var(--color-bg-surface);
    color: var(--color-text-main);
}

.btn--ghost:hover {
    background: var(--button-hover);
}

.btn--primary {
    border: 1px solid var(--color-word-blue-dark);
    background: var(--color-word-blue);
    color: var(--color-text-on-blue);
    font-weight: 600;
}

.btn--primary:hover {
    background: var(--color-word-blue-dark);
}

.btn--primary:disabled {
    opacity: 0.6;
    cursor: default;
}

.btn:focus-visible {
    outline: 2px solid var(--color-word-blue-dark);
    outline-offset: 2px;
}

.update-fade-enter-active,
.update-fade-leave-active {
    transition: opacity 0.18s ease;
}

.update-fade-enter-from,
.update-fade-leave-to {
    opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
    .bar__fill {
        transition: none;
    }
}
</style>
