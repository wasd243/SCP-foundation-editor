<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import {
    inputWindowState,
    resolveInputWindow,
} from "../../stores/inputWindow.ts";

const value = ref("");
const inputRef = ref<HTMLInputElement | null>(null);

// Remember whatever held focus before the dialog opened so we can restore it
// when the dialog closes.
let previouslyFocused: HTMLElement | null = null;

watch(
    () => inputWindowState.visible,
    (visible) => {
        if (visible) {
            previouslyFocused =
                document.activeElement instanceof HTMLElement
                    ? document.activeElement
                    : null;
            value.value = inputWindowState.defaultValue;
            nextTick(() => {
                inputRef.value?.focus();
                inputRef.value?.select();
            });
        } else {
            previouslyFocused?.focus();
            previouslyFocused = null;
        }
    },
);

function confirm() {
    // Empty input is treated as a cancel, matching the previous prompt() flow
    // where an empty value inserted nothing.
    resolveInputWindow(value.value.trim() || null);
}

function cancel() {
    resolveInputWindow(null);
}
</script>

<template>
    <Teleport to="body">
        <div
            v-if="inputWindowState.visible"
            class="input-window-backdrop"
            @pointerdown.self="cancel"
        >
            <div
                class="input-window"
                role="dialog"
                aria-modal="true"
                aria-labelledby="input-window-title"
                @keydown.esc.prevent="cancel"
            >
                <div class="input-window-accent" aria-hidden="true"></div>
                <div class="input-window-body">
                    <h2 id="input-window-title" class="input-window-title">
                        {{ inputWindowState.title }}
                    </h2>
                    <label
                        v-if="inputWindowState.label"
                        class="input-window-label"
                        for="input-window-field"
                    >
                        {{ inputWindowState.label }}
                    </label>
                    <input
                        id="input-window-field"
                        ref="inputRef"
                        v-model="value"
                        class="input-window-field"
                        type="text"
                        :placeholder="inputWindowState.placeholder"
                        autocomplete="off"
                        spellcheck="false"
                        @keydown.enter.prevent="confirm"
                    />
                    <div class="input-window-actions">
                        <button
                            type="button"
                            class="input-window-button is-secondary"
                            @click="cancel"
                        >
                            Cancel
                        </button>
                        <button
                            type="button"
                            class="input-window-button is-primary"
                            @click="confirm"
                        >
                            {{ inputWindowState.confirmText }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
.input-window-backdrop {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: rgba(17, 24, 39, 0.45);
}

.input-window {
    width: min(420px, 100%);
    overflow: hidden;
    background: var(--color-bg-surface);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.25);
    font-family: var(--font-ui);
    animation: input-window-in 0.12s ease;
}

/* The single bit of color: a thin Word-blue strip at the top of the dialog. */
.input-window-accent {
    height: 3px;
    background: var(--color-word-blue);
}

.input-window-body {
    padding: 18px 20px 16px;
}

.input-window-title {
    margin: 0 0 12px;
    font-size: 15px;
    font-weight: 600;
    color: var(--color-text-main);
}

.input-window-label {
    display: block;
    margin-bottom: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--context-menu-muted);
}

.input-window-field {
    width: 100%;
    box-sizing: border-box;
    padding: 8px 10px;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    color: var(--color-text-main);
    font-family: inherit;
    font-size: 14px;
    outline: none;
}

.input-window-field:focus {
    border-color: var(--color-word-blue);
    box-shadow: 0 0 0 2px var(--color-word-blue-light);
}

.input-window-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 18px;
}

.input-window-button {
    min-width: 76px;
    padding: 7px 14px;
    border-radius: 3px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

.input-window-button:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}

.input-window-button.is-secondary {
    border: 1px solid var(--color-border);
    background: var(--color-bg-surface);
    color: var(--color-text-main);
}

.input-window-button.is-secondary:hover {
    background: var(--button-hover);
}

.input-window-button.is-primary {
    border: 1px solid var(--color-word-blue);
    background: var(--color-word-blue);
    color: var(--color-text-on-blue);
}

.input-window-button.is-primary:hover {
    background: var(--color-word-blue-dark);
    border-color: var(--color-word-blue-dark);
}

@keyframes input-window-in {
    from {
        transform: translateY(-6px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@media (prefers-reduced-motion: reduce) {
    .input-window {
        animation: none;
    }
}
</style>
