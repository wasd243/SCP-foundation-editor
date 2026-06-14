<script setup lang="ts">
import { insertEditorFootnote } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnFootnote.ts";
</script>

<template>
    <button class="component-card" type="button" @click="insertEditorFootnote">
        <!--Hardcoded svg icon, not planned to move because I didn't find any good `Footnote` icons in SvgRepo-->
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <text
                x="5"
                y="8"
                font-size="9"
                font-family="serif"
                fill="currentColor"
            >
                1
            </text>
            <line
                x1="4"
                y1="11"
                x2="16"
                y2="11"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
            />
            <line
                x1="4"
                y1="15"
                x2="13"
                y2="15"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
            />
        </svg>
        Footnotes
    </button>
</template>
