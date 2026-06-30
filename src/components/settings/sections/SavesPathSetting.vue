<script setup lang="ts">
import { onMounted } from "vue";
import {
    loadSavesPath,
    openSavesFolder,
    pickSavesFolder,
    resetSavesPath,
    savesPath,
    savesPathError,
} from "../../../stores/btnToolBar/settings/savesPath.ts";

onMounted(loadSavesPath);
</script>

<template>
    <section class="saves-setting" aria-label="Saves folder settings">
        <header class="saves-setting__eyebrow">Saves folder</header>

        <p class="saves-setting__path" :title="savesPath">
            {{ savesPath || "resolving…" }}
        </p>

        <div class="saves-setting__controls" role="group">
            <button class="saves-chip" type="button" @click="pickSavesFolder">
                Choose folder…
            </button>
            <button class="saves-chip" type="button" @click="openSavesFolder">
                Open folder
            </button>
            <button class="saves-chip" type="button" @click="resetSavesPath">
                Reset to default
            </button>
        </div>

        <p v-if="savesPathError" class="saves-setting__error">
            {{ savesPathError }}
        </p>
    </section>
</template>

<style scoped>
.saves-setting {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 12px 0 12px;
    font-family: var(--font-ui);
    color: var(--color-text-main);
    user-select: none;
}

.saves-setting__eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #5f6b7a;
}

.saves-setting__path {
    margin: 0;
    max-width: 320px;
    font-size: 12px;
    color: #5f6b7a;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.saves-setting__controls {
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

.saves-chip:focus-visible {
    outline: 2px solid var(--color-word-blue);
    outline-offset: 2px;
}

.saves-setting__error {
    margin: 0;
    font-size: 12px;
    color: var(--wikidot-red);
}
</style>
