<script setup lang="ts">
import { computed } from "vue";
import {
    status,
    newVersion,
    dismissed,
    dismissBanner,
    openUpdateDialog,
    downloadAndInstallUpdate,
} from "../../stores/updater.ts";

// Word's "document notification" idiom: a slim bar under the ribbon, shown only
// while an update is waiting to be acted on and the user hasn't dismissed it.
const visible = computed(
    () =>
        (status.value === "available" || status.value === "downloaded") &&
        !dismissed.value,
);

const ready = computed(() => status.value === "downloaded");

function install() {
    if (ready.value) {
        openUpdateDialog();
    } else {
        void downloadAndInstallUpdate();
        openUpdateDialog();
    }
}
</script>

<template>
    <Transition name="update-bar">
        <aside
            v-if="visible"
            class="update-bar"
            role="status"
            aria-live="polite"
        >
            <span class="update-bar__dot" aria-hidden="true"></span>

            <p class="update-bar__msg">
                <template v-if="ready">
                    SCP-WYSIWYG <strong>v{{ newVersion }}</strong> is downloaded
                    and ready to install.
                </template>
                <template v-else>
                    A new version,
                    <strong>v{{ newVersion }}</strong
                    >, is available.
                </template>
            </p>

            <div class="update-bar__actions">
                <button
                    class="update-bar__link"
                    type="button"
                    @click="openUpdateDialog"
                >
                    What's new
                </button>
                <button
                    class="update-bar__cta"
                    type="button"
                    @click="install"
                >
                    {{ ready ? "Restart…" : "Install update" }}
                </button>
                <button
                    class="update-bar__close"
                    type="button"
                    aria-label="Dismiss update notice"
                    @click="dismissBanner"
                >
                    ✕
                </button>
            </div>
        </aside>
    </Transition>
</template>

<style scoped>
.update-bar {
    flex: 0 0 auto;
    z-index: 15;

    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 12px 7px 14px;

    background: var(--color-word-blue-light);
    border-bottom: 1px solid var(--color-border);
    border-left: 3px solid var(--color-word-blue);

    font-family: var(--font-ui);
    color: var(--color-text-main);
}

.update-bar__dot {
    width: 8px;
    height: 8px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--color-word-blue);
}

.update-bar__msg {
    margin: 0;
    flex: 1 1 auto;
    font-size: 13px;
    min-width: 0;
}

.update-bar__msg strong {
    font-family: ui-monospace, "Cascadia Code", "Consolas", monospace;
    font-weight: 700;
}

.update-bar__actions {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.update-bar__link {
    border: 0;
    background: transparent;
    color: var(--color-word-blue);
    font: inherit;
    font-size: 13px;
    text-decoration: underline;
    cursor: pointer;
    padding: 4px 6px;
}

.update-bar__cta {
    border: 1px solid var(--color-word-blue-dark);
    border-radius: 3px;
    background: var(--color-word-blue);
    color: var(--color-text-on-blue);
    font: inherit;
    font-size: 13px;
    font-weight: 600;
    padding: 5px 12px;
    cursor: pointer;
    transition: background 0.12s ease;
}

.update-bar__cta:hover {
    background: var(--color-word-blue-dark);
}

.update-bar__close {
    border: 0;
    background: transparent;
    color: #5f6b7a;
    font-size: 13px;
    line-height: 1;
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 3px;
}

.update-bar__close:hover {
    background: rgba(15, 63, 143, 0.1);
}

.update-bar__link:focus-visible,
.update-bar__cta:focus-visible,
.update-bar__close:focus-visible {
    outline: 2px solid var(--color-word-blue-dark);
    outline-offset: 2px;
}

/* Slide-in under the ribbon. */
.update-bar-enter-active,
.update-bar-leave-active {
    transition:
        transform 0.22s ease,
        opacity 0.22s ease;
}

.update-bar-enter-from,
.update-bar-leave-to {
    transform: translateY(-100%);
    opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
    .update-bar-enter-active,
    .update-bar-leave-active {
        transition: opacity 0.15s ease;
    }
    .update-bar-enter-from,
    .update-bar-leave-to {
        transform: none;
    }
}
</style>
