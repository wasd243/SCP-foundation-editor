<script setup lang="ts">
import OrderedList from "../../../../../assets/icons/OrderedList.svg";
import { activeFormats } from "../../../../../stores/btnToolBar/activeFormats.ts";

const emit = defineEmits<{
    toggle: [];
}>();
</script>

<template>
    <button
        class="format-basic-button list-ol"
        :class="{ active: activeFormats.orderedList }"
        type="button"
        @click="emit('toggle')"
    >
        <img :src="OrderedList" alt="OrderedList" />
    </button>
</template>
