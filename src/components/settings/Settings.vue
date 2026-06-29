<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import {
    settingsOpen,
    activeCategory,
    closeSettings,
    type SettingsCategory,
} from "../../stores/settingsWindow.ts";

import AutoSaveSetting from "./sections/AutoSaveSetting.vue";
import SavesPathSetting from "./sections/SavesPathSetting.vue";
import InvisibleCharactersSetting from "./sections/InvisibleCharactersSetting.vue";
import LogAndWriteJson from "./sections/LogAndWriteJson.vue";
import UpdateSetting from "./sections/UpdateSetting.vue";

const CATEGORIES: { id: SettingsCategory; label: string }[] = [
    { id: "save", label: "Save" },
    { id: "display", label: "Display" },
    { id: "advanced", label: "Advanced" },
    { id: "updates", label: "Updates" },
];

const activeLabel = () =>
    CATEGORIES.find((c) => c.id === activeCategory.value)?.label ?? "";

const dialogRef = ref<HTMLElement | null>(null);

// Remember what held focus before opening so we can hand it back on close —
// same courtesy InputWindow.vue extends.
let previouslyFocused: HTMLElement | null = null;

watch(settingsOpen, (open) => {
    if (open) {
        previouslyFocused =
            document.activeElement instanceof HTMLElement
                ? document.activeElement
                : null;
        nextTick(() => dialogRef.value?.focus());
    } else {
        previouslyFocused?.focus();
        previouslyFocused = null;
    }
});
</script>

<template>
    <Teleport to="body">
        <Transition name="settings-fade">
            <div
                v-if="settingsOpen"
                class="settings-backdrop"
                @pointerdown.self="closeSettings"
            >
                <div
                    ref="dialogRef"
                    class="settings-modal"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="settings-title"
                    tabindex="-1"
                    @keydown.esc.prevent="closeSettings"
                >
                    <header class="settings-modal__head">
                        <h2 id="settings-title" class="settings-modal__title">
                            Settings
                        </h2>
                        <button
                            class="settings-modal__close"
                            type="button"
                            aria-label="Close"
                            @click="closeSettings"
                        >
                            ✕
                        </button>
                    </header>

                    <div class="settings-modal__body">
                        <nav class="settings-rail" aria-label="Settings categories">
                            <button
                                v-for="cat in CATEGORIES"
                                :key="cat.id"
                                class="settings-rail__item"
                                :class="{ 'is-active': activeCategory === cat.id }"
                                type="button"
                                :aria-current="
                                    activeCategory === cat.id ? 'true' : undefined
                                "
                                @click="activeCategory = cat.id"
                            >
                                {{ cat.label }}
                            </button>
                        </nav>

                        <section
                            class="settings-pane"
                            :aria-label="activeLabel()"
                        >
                            <h3 class="settings-pane__title">{{ activeLabel() }}</h3>

                            <template v-if="activeCategory === 'save'">
                                <AutoSaveSetting />
                                <div
                                    class="settings-pane__divider"
                                    aria-hidden="true"
                                ></div>
                                <SavesPathSetting />
                            </template>

                            <template v-else-if="activeCategory === 'display'">
                                <InvisibleCharactersSetting />
                            </template>

                            <template v-else-if="activeCategory === 'advanced'">
                                <LogAndWriteJson />
                            </template>

                            <template v-else>
                                <UpdateSetting />
                            </template>
                        </section>
                    </div>

                    <footer class="settings-modal__foot">
                        <button
                            class="btn btn--primary"
                            type="button"
                            @click="closeSettings"
                        >
                            Close
                        </button>
                    </footer>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.settings-backdrop {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.42);
    font-family: var(--font-ui);
}

.settings-modal {
    width: min(720px, calc(100vw - 32px));
    height: min(560px, calc(100vh - 64px));
    display: flex;
    flex-direction: column;
    background: var(--color-bg-surface);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28);
    color: var(--color-text-main);
    overflow: hidden;
}

.settings-modal:focus {
    outline: none;
}

/* --- Header: shared blue chrome with UpdateDialog --- */
.settings-modal__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex: 0 0 auto;
    padding: 12px 14px;
    background: var(--color-word-blue);
}

.settings-modal__title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-on-blue);
}

.settings-modal__close {
    border: 0;
    background: transparent;
    color: var(--color-text-on-blue);
    font-size: 14px;
    line-height: 1;
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 3px;
}

.settings-modal__close:hover {
    background: rgba(255, 255, 255, 0.18);
}

.settings-modal__close:focus-visible {
    outline: 2px solid var(--color-text-on-blue);
    outline-offset: 1px;
}

/* --- Body: two-pane Word Options layout --- */
.settings-modal__body {
    flex: 1 1 auto;
    display: flex;
    min-height: 0;
}

.settings-rail {
    flex: 0 0 176px;
    display: flex;
    flex-direction: column;
    padding: 8px 0;
    background: var(--color-bg-app);
    border-right: 1px solid var(--color-border);
    overflow-y: auto;
}

.settings-rail__item {
    position: relative;
    text-align: left;
    padding: 8px 16px 8px 17px;
    border: 0;
    background: transparent;
    color: var(--color-text-main);
    font: inherit;
    font-size: 13px;
    cursor: pointer;
}

.settings-rail__item:hover {
    background: var(--button-hover);
}

/* The signature: a 3px Word-blue bar + soft tint marks the active category. */
.settings-rail__item.is-active {
    background: var(--color-word-blue-light);
    color: var(--color-word-blue);
    font-weight: 600;
}

.settings-rail__item.is-active::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 3px;
    background: var(--color-word-blue);
}

.settings-rail__item:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: -2px;
}

.settings-pane {
    flex: 1 1 auto;
    overflow-y: auto;
    padding: 18px 22px;
}

.settings-pane__title {
    margin: 0 0 16px;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-main);
}

.settings-pane__divider {
    height: 1px;
    margin: 16px 0;
    background: var(--group-border);
}

/* --- Footer: shared button styling with UpdateDialog --- */
.settings-modal__foot {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex: 0 0 auto;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid var(--color-border);
}

.btn {
    font: inherit;
    font-size: 13px;
    padding: 6px 16px;
    border-radius: 3px;
    cursor: pointer;
    transition:
        background 0.12s ease,
        border-color 0.12s ease;
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

.btn:focus-visible {
    outline: 2px solid var(--color-word-blue-dark);
    outline-offset: 2px;
}

.settings-fade-enter-active,
.settings-fade-leave-active {
    transition: opacity 0.18s ease;
}

.settings-fade-enter-from,
.settings-fade-leave-to {
    opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
    .settings-fade-enter-active,
    .settings-fade-leave-active {
        transition: none;
    }
}
</style>
