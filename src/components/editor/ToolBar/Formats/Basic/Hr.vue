<script setup lang="ts">
import Hr from "../../../../../assets/icons/Hr.svg";

const emit = defineEmits<{
  insert: [];
}>();
</script>

<template>
  <button class="format-basic-button hr" type="button" @click="emit('insert')">
    <img :src="Hr" alt="Hr" />
  </button>
</template>
