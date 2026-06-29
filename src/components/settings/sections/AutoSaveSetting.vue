<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import {
    AUTO_SAVE_MIN_SECONDS,
    autoSaveEnabled,
    autoSaveError,
    autoSaveIntervalSeconds,
    autoSaveLastSavedAt,
    setAutoSaveInterval,
    toggleAutoSave,
} from "../../../stores/btnToolBar/btnActions/btnAutoSave.ts";

const PRESETS = [
    { label: "30s", seconds: 30 },
    { label: "1 min", seconds: 60 },
    { label: "5 min", seconds: 300 },
];

// Local editable copy for the custom number field; commit on change/blur.
const draft = ref(autoSaveIntervalSeconds.value);
watch(autoSaveIntervalSeconds, (v) => {
    draft.value = v;
});

function commitDraft() {
    setAutoSaveInterval(Number(draft.value));
}

// Ticking clock so the "last saved" label stays relative without manual refresh.
const now = ref(Date.now());
let clock: number | null = null;
onMounted(() => {
    clock = window.setInterval(() => (now.value = Date.now()), 1000);
});
onUnmounted(() => {
    if (clock !== null) clearInterval(clock);
});

const lastSavedLabel = computed(() => {
    if (autoSaveLastSavedAt.value === null) return "no saves yet";
    const secs = Math.max(0, Math.round((now.value - autoSaveLastSavedAt.value) / 1000));
    if (secs < 3) return "saved just now";
    if (secs < 60) return `saved ${secs}s ago`;
    return `saved ${Math.floor(secs / 60)}m ago`;
});

const statusText = computed(() => {
    if (autoSaveError.value) return "save failed — check the saves\\ folder";
    if (!autoSaveEnabled.value) return "off";
    return lastSavedLabel.value;
});
</script>

<template>
    <section class="autosave-setting" aria-label="Auto-save settings">
        <header class="autosave-setting__eyebrow">Auto-save</header>

        <div class="autosave-setting__controls">
            <button
                class="autosave-switch"
                :class="{ 'is-on': autoSaveEnabled }"
                type="button"
                role="switch"
                :aria-checked="autoSaveEnabled"
                @click="toggleAutoSave"
            >
                <span class="autosave-switch__track">
                    <span class="autosave-switch__thumb"></span>
                </span>
                <span class="autosave-switch__text">{{
                    autoSaveEnabled ? "On" : "Off"
                }}</span>
            </button>

            <div class="autosave-setting__interval">
                <span class="autosave-setting__field-label">Every</span>

                <div class="autosave-presets" role="group" aria-label="Interval presets">
                    <button
                        v-for="preset in PRESETS"
                        :key="preset.seconds"
                        class="autosave-chip"
                        :class="{
                            'is-active': autoSaveIntervalSeconds === preset.seconds,
                        }"
                        type="button"
                        @click="setAutoSaveInterval(preset.seconds)"
                    >
                        {{ preset.label }}
                    </button>
                </div>

                <label class="autosave-custom">
                    <input
                        v-model.number="draft"
                        class="autosave-custom__input"
                        type="number"
                        :min="AUTO_SAVE_MIN_SECONDS"
                        step="5"
                        inputmode="numeric"
                        aria-label="Custom interval in seconds"
                        @change="commitDraft"
                        @blur="commitDraft"
                    />
                    <span class="autosave-custom__unit">sec</span>
                </label>
            </div>
        </div>

        <p
            class="autosave-setting__status"
            :class="{
                'is-on': autoSaveEnabled && !autoSaveError,
                'has-error': autoSaveError,
            }"
        >
            <span class="autosave-setting__dot" aria-hidden="true"></span>
            <span>{{ statusText }}</span>
        </p>
    </section>
</template>

<style scoped>
.autosave-setting {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 12px 0 0;
    font-family: var(--font-ui);
    color: var(--color-text-main);
    user-select: none;
}

.autosave-setting__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

.autosave-setting__controls {
    display: flex;
    align-items: center;
    gap: 16px;
}

/* --- On/off switch --- */
.autosave-switch {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    color: inherit;
    font: inherit;
}

.autosave-switch__track {
    position: relative;
    width: 34px;
    height: 18px;
    border-radius: 9px;
    background: #c8d3e6;
    transition: background 0.14s ease;
}

.autosave-switch.is-on .autosave-switch__track {
    background: var(--color-word-blue);
}

.autosave-switch__thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
    transition: transform 0.14s ease;
}

.autosave-switch.is-on .autosave-switch__thumb {
    transform: translateX(16px);
}

.autosave-switch__text {
    font-size: 12px;
    font-weight: 600;
    min-width: 20px;
    text-align: left;
}

/* --- Interval --- */
.autosave-setting__interval {
    display: flex;
    align-items: center;
    gap: 8px;
}

.autosave-setting__field-label {
    font-size: 12px;
    color: #5f6b7a;
}

.autosave-presets {
    display: inline-flex;
    gap: 4px;
}

.autosave-chip {
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

.autosave-chip:hover {
    background: var(--button-hover);
}

.autosave-chip.is-active {
    background: var(--color-word-blue);
    border-color: var(--color-word-blue-dark);
    color: var(--color-text-on-blue);
}

.autosave-custom {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.autosave-custom__input {
    width: 52px;
    padding: 3px 6px;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    color: var(--color-text-main);
    font: inherit;
    font-size: 12px;
}

.autosave-custom__input:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 0;
    border-color: var(--color-word-blue);
}

.autosave-custom__unit {
    font-size: 12px;
    color: #5f6b7a;
}

/* --- Status line --- */
.autosave-setting__status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0;
    font-size: 12px;
    color: #7a8492;
}

.autosave-setting__dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: transparent;
    box-shadow: inset 0 0 0 1.5px var(--color-autosave-idle);
}

.autosave-setting__status.is-on .autosave-setting__dot {
    background: var(--color-autosave-live);
    box-shadow: none;
}

.autosave-setting__status.is-on {
    color: var(--color-text-main);
}

.autosave-setting__status.has-error {
    color: var(--wikidot-red);
}

.autosave-setting__status.has-error .autosave-setting__dot {
    background: var(--wikidot-red);
    box-shadow: none;
}

/* Keyboard focus visibility */
.autosave-switch:focus-visible,
.autosave-chip:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}
</style>
