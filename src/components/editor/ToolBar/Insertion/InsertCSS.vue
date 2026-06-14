<script setup lang="ts">
import InsertCss from "../../../../assets/icons/InsertCSS.svg";
import { ref } from "vue";
import CSSPanel from "./CSSPanel.vue";
const showCSSPanel = ref(false);
</script>

<template>
    <button
        class="format-insertion-button css-button"
        type="button"
        @click="showCSSPanel = true"
    >
        <img :src="InsertCss" alt="Insert CSS" />
        <br />
        Module CSS
    </button>
    <CSSPanel v-if="showCSSPanel" @close="showCSSPanel = false" />
</template>
