<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { LogAndWriteJson } from "../../../../stores/btnToolBar/btnActions/btnLogAndWriteJson.ts";

const OUTPUT_PATH = "temp/dev_output.json";

const hasWritten = ref(false);
const justWrote = ref(false);
const failed = ref(false);
let clearPulse: number | null = null;

async function writeSnapshot() {
    failed.value = false;
    try {
        await LogAndWriteJson();
        hasWritten.value = true;
        justWrote.value = true;
        if (clearPulse !== null) clearTimeout(clearPulse);
        clearPulse = window.setTimeout(() => (justWrote.value = false), 2400);
    } catch {
        failed.value = true;
    }
}

onUnmounted(() => {
    if (clearPulse !== null) clearTimeout(clearPulse);
});

// The status line doubles as the destination: it normally shows where the file
// lands, and only swaps to an actionable message when the write fails.
const statusText = computed(() => {
    if (failed.value) return "Write failed — check temp/ is writable";
    return OUTPUT_PATH;
});
</script>

<template>
    <section class="devtools" aria-label="Developer tools">
        <header class="devtools__eyebrow">Developer</header>

        <button
            class="devtools__dump"
            :class="{ 'is-ok': justWrote, 'has-error': failed }"
            type="button"
            @click="writeSnapshot"
        >
            <span class="devtools__caret" aria-hidden="true">&gt;</span>
            <span class="devtools__label">Write JSON snapshot</span>
        </button>

        <p
            class="devtools__status"
            :class="{ 'is-ok': justWrote, 'has-error': failed }"
        >
            <span class="devtools__dot" aria-hidden="true"></span>
            <span class="devtools__path">{{ statusText }}</span>
        </p>
    </section>
</template>

<style scoped>
.devtools {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 0 0 14px;
    font-family: var(--font-ui), sans-serif;
    color: var(--color-text-main);
    user-select: none;
}

.devtools__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

/* The console chip: the one bold element. Dark surface + mono + caret reads as
   an editor-side instrument, distinct from the user-facing auto-save switch. */
.devtools__dump {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    align-self: flex-start;
    padding: 6px 12px 6px 10px;
    border: 1px solid #2c3947;
    border-radius: 4px;
    background: #1f2733;
    color: #e6edf3;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: -0.1px;
    line-height: 1;
    cursor: pointer;
    transition:
        background 0.14s ease,
        border-color 0.14s ease,
        transform 0.06s ease;
}

.devtools__dump:hover {
    background: #273341;
    border-color: var(--color-word-blue);
}

.devtools__dump:active {
    transform: translateY(1px);
    background: #1a212b;
}

.devtools__dump:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}

.devtools__caret {
    color: #5aa2ff;
    font-weight: 700;
}

.devtools__dump.is-ok .devtools__caret {
    color: var(--color-autosave-live);
}

.devtools__dump.has-error {
    border-color: var(--wikidot-red);
}

.devtools__label {
    white-space: nowrap;
}

/* Status line mirrors the auto-save group: a state dot plus muted text. Here the
   text is the live destination path, so the control says exactly where it writes. */
.devtools__status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0;
    font-size: 12px;
    color: #7a8492;
}

.devtools__path {
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 11px;
}

.devtools__status.has-error .devtools__path {
    font-family: var(--font-ui), sans-serif;
}

.devtools__dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: transparent;
    box-shadow: inset 0 0 0 1.5px var(--color-autosave-idle);
}

.devtools__status.is-ok {
    color: var(--color-text-main);
}

.devtools__status.is-ok .devtools__dot {
    background: var(--color-autosave-live);
    box-shadow: none;
    animation: devtools-pulse 2.4s ease-out;
}

.devtools__status.has-error {
    color: var(--wikidot-red);
}

.devtools__status.has-error .devtools__dot {
    background: var(--wikidot-red);
    box-shadow: none;
}

@keyframes devtools-pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(31, 170, 89, 0.45);
    }
    40% {
        box-shadow: 0 0 0 5px rgba(31, 170, 89, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(31, 170, 89, 0);
    }
}

@media (prefers-reduced-motion: reduce) {
    .devtools__dump,
    .devtools__dump:active {
        transition: none;
        transform: none;
    }

    .devtools__status.is-ok .devtools__dot {
        animation: none;
    }
}
</style>
