<script setup lang="ts">
import { ref } from "vue";
import { getEditor } from "../../../stores/editor.ts";
import { useEditorSubscription } from "../../../composables/useEditorSubscription.ts";

// Source of truth is the ProseMirror plugin's own visibility flag; this ref is
// only a mirror kept in lockstep with it. `visibility()` can be undefined for a
// tick before the extension's onBeforeCreate runs, so default to shown.
const visible = ref(true);

function syncVisibility() {
    const v = getEditor()?.storage.invisibleCharacters?.visibility?.();
    visible.value = v ?? true;
}

// The toggle command dispatches a meta transaction, which fires "transaction",
// so this subscription re-reads the flag and the switch follows the document.
useEditorSubscription(syncVisibility);

function toggle() {
    getEditor()?.commands.toggleInvisibleCharacters();
}
</script>

<template>
    <section class="marks-setting" aria-label="Formatting marks">
        <header class="marks-setting__eyebrow">Formatting marks</header>

        <button
            class="marks-switch"
            :class="{ 'is-on': visible }"
            type="button"
            role="switch"
            :aria-checked="visible"
            @click="toggle"
        >
            <span class="marks-switch__track">
                <span class="marks-switch__thumb"></span>
            </span>
            <span class="marks-switch__text">{{ visible ? "On" : "Off" }}</span>
        </button>

        <!-- The signature: a miniature editor line. The return glyph is inked
             when marks are shown and ghosted when hidden — exactly what the
             writer sees happen to paragraph ends in the canvas. -->
        <div
            class="marks-specimen"
            :class="{ 'is-shown': visible }"
            aria-hidden="true"
        >
            <span class="marks-specimen__text">The hatch sealed behind us</span>
            <span class="marks-specimen__glyph">↵</span>
        </div>

        <p class="marks-setting__legend">End of every paragraph</p>
    </section>
</template>

<style scoped>
.marks-setting {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 12px 0 12px;
    font-family: var(--font-ui);
    color: var(--color-text-main);
    user-select: none;
}

.marks-setting__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

/* --- On/off switch: pixel-identical to the Auto-save switch for cohesion --- */
.marks-switch {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    align-self: flex-start;
    padding: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    color: inherit;
    font: inherit;
}

.marks-switch__track {
    position: relative;
    width: 34px;
    height: 18px;
    border-radius: 9px;
    background: #c8d3e6;
    transition: background 0.14s ease;
}

.marks-switch.is-on .marks-switch__track {
    background: var(--color-word-blue);
}

.marks-switch__thumb {
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

.marks-switch.is-on .marks-switch__thumb {
    transform: translateX(16px);
}

.marks-switch__text {
    font-size: 12px;
    font-weight: 600;
    min-width: 20px;
    text-align: left;
}

/* --- Specimen --- */
.marks-specimen {
    display: inline-flex;
    align-items: baseline;
    align-self: flex-start;
    max-width: 240px;
    padding: 5px 9px;
    border: 1px solid var(--color-border);
    border-radius: 3px;
    background: var(--color-bg-surface);
    font-size: 13px;
    line-height: 1.2;
}

.marks-specimen__text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--color-text-main);
}

/* The glyph carries the state: faint when hidden, fully inked when shown. */
.marks-specimen__glyph {
    margin-left: 1px;
    color: var(--color-word-blue);
    opacity: 0.16;
    transition: opacity 0.14s ease;
}

.marks-specimen.is-shown .marks-specimen__glyph {
    opacity: 1;
}

/* --- Legend: names the mark instead of echoing on/off --- */
.marks-setting__legend {
    margin: 0;
    font-size: 12px;
    color: #5f6b7a;
}

.marks-switch:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
    .marks-switch__track,
    .marks-switch__thumb,
    .marks-specimen__glyph {
        transition: none;
    }
}
</style>
