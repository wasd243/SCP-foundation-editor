<script setup lang="ts">
import UnorderedList from "../../../../../assets/icons/UnorderedList.svg";
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button list-ul"
        :class="{ active: activeFormats.bulletList }"
        type="button"
        @click="emit('toggle')"
    >
        <img :src="UnorderedList" alt="UnorderedList" />
    </button>
</template>
