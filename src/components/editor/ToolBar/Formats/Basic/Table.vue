<script setup lang="ts">
import Table from "../../../../../assets/icons/Table.svg";

const emit = defineEmits<{
    insert: [];
}>();
</script>

<template>
    <button
        class="format-basic-button table"
        type="button"
        @click="emit('insert')"
    >
        <img :src="Table" alt="Table" />
    </button>
</template>
