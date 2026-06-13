<script setup lang="ts">
import OrderedList from "../../../../../assets/icons/OrderedList.svg";

const emit = defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <button class="format-basic-button list-ol" type="button" @click="emit('toggle')">
    <img :src="OrderedList" alt="OrderedList" />
  </button>
</template>
