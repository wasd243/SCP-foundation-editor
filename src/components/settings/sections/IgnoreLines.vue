<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
    ignoreRanges,
    ignoreLinesError,
    loadIgnoreLines,
    addIgnoreLine,
    removeIgnoreLine,
    formatRange,
} from "../../../stores/btnToolBar/settings/ignoreLines.ts";

const draft = ref("");

onMounted(loadIgnoreLines);

async function commit() {
    const accepted = await addIgnoreLine(draft.value);
    if (accepted) draft.value = "";
}
</script>

<template>
    <section class="ignore-lines" aria-label="Ignored lines">
        <header class="ignore-lines__eyebrow">Ignored lines</header>
        <p class="ignore-lines__help">Skip these source lines when exporting.</p>

        <ul v-if="ignoreRanges.length" class="ignore-lines__list">
            <li
                v-for="(range, i) in ignoreRanges"
                :key="`${range.start}-${range.end}`"
                class="ignore-row"
            >
                <span class="ignore-row__value">{{ formatRange(range) }}</span>
                <button
                    class="ignore-row__remove"
                    type="button"
                    :aria-label="`Remove ${formatRange(range)}`"
                    @click="removeIgnoreLine(i)"
                >
                    ✕
                </button>
            </li>
        </ul>
        <p v-else class="ignore-lines__empty">
            No ignored lines yet. Add a line number like 7, or a range like 1-10.
        </p>

        <div class="ignore-lines__add">
            <input
                v-model="draft"
                class="ignore-lines__input"
                type="text"
                inputmode="numeric"
                placeholder="e.g. 1-10 or 7"
                aria-label="Add a line number or range"
                autocomplete="off"
                spellcheck="false"
                @keydown.enter.prevent="commit"
            />
            <button
                class="ignore-lines__plus"
                type="button"
                aria-label="Add"
                @click="commit"
            >
                +
            </button>
        </div>

        <p v-if="ignoreLinesError" class="ignore-lines__error">
            {{ ignoreLinesError }}
        </p>
    </section>
</template>

<style scoped>
.ignore-lines {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 0 0;
    font-family: var(--font-ui);
    color: var(--color-text-main);
    user-select: none;
    max-width: 360px;
}

.ignore-lines__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

.ignore-lines__help {
    margin: 0 0 4px;
    font-size: 12px;
    color: #5f6b7a;
}

/* --- Saved ranges: each row reads like a line in a code gutter --- */
.ignore-lines__list {
    list-style: none;
    margin: 0;
    padding: 0;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    overflow: hidden;
}

.ignore-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 8px 6px 0;
}

.ignore-row + .ignore-row {
    border-top: 1px solid var(--color-border);
}

/* The signature: a Word-blue gutter tick, then the value in tabular monospace. */
.ignore-row__value {
    position: relative;
    flex: 1 1 auto;
    padding-left: 13px;
    font-family: ui-monospace, "Cascadia Code", "Consolas", monospace;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    color: var(--color-text-main);
}

.ignore-row__value::before {
    content: "";
    position: absolute;
    top: 1px;
    bottom: 1px;
    left: 6px;
    width: 2px;
    border-radius: 1px;
    background: var(--color-word-blue);
}

.ignore-row__remove {
    flex: 0 0 auto;
    width: 20px;
    height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 3px;
    background: transparent;
    color: #7a8492;
    font-size: 11px;
    line-height: 1;
    cursor: pointer;
    opacity: 0;
    transition:
        opacity 0.12s ease,
        background 0.12s ease,
        color 0.12s ease;
}

.ignore-row:hover .ignore-row__remove,
.ignore-row__remove:focus-visible {
    opacity: 1;
}

.ignore-row__remove:hover {
    background: var(--button-hover);
    color: var(--wikidot-red);
}

.ignore-row__remove:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 1px;
}

.ignore-lines__empty {
    margin: 0;
    padding: 10px 12px;
    border: 1px dashed var(--color-border);
    border-radius: 3px;
    font-size: 12px;
    color: #5f6b7a;
}

/* --- Add row --- */
.ignore-lines__add {
    display: flex;
    gap: 6px;
    margin-top: 2px;
}

.ignore-lines__input {
    flex: 1 1 auto;
    min-width: 0;
    padding: 5px 9px;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    color: var(--color-text-main);
    font: inherit;
    font-size: 13px;
}

.ignore-lines__input:focus {
    outline: none;
    border-color: var(--color-word-blue);
    box-shadow: 0 0 0 2px var(--color-word-blue-light);
}

.ignore-lines__plus {
    flex: 0 0 auto;
    width: 30px;
    border: 1px solid var(--color-word-blue-dark);
    border-radius: 3px;
    background: var(--color-word-blue);
    color: var(--color-text-on-blue);
    font-size: 16px;
    font-weight: 600;
    line-height: 1;
    cursor: pointer;
    transition: background 0.12s ease;
}

.ignore-lines__plus:hover {
    background: var(--color-word-blue-dark);
}

.ignore-lines__plus:focus-visible {
    outline: 2px solid var(--color-word-blue-dark);
    outline-offset: 2px;
}

.ignore-lines__error {
    margin: 0;
    font-size: 12px;
    color: var(--wikidot-red);
}

@media (prefers-reduced-motion: reduce) {
    .ignore-row__remove {
        transition: none;
        opacity: 1;
    }
}
</style>
