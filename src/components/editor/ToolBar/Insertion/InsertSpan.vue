<script setup lang="ts">
// Use the same icon as InsertDiv
import InsertSpan from "../../../../assets/icons/InsertDiv.svg";
import { ref } from "vue";
import SpanPanel from "./SpanPanel.vue";
const showSpanPanel = ref(false);
</script>

<template>
    <button
        class="format-insertion-button span-button"
        type="button"
        @click="showSpanPanel = true"
    >
        <img :src="InsertSpan" alt="InsertSpan" />
        <br />
        Span
    </button>
    <SpanPanel v-if="showSpanPanel" @close="showSpanPanel = false" />
</template>
