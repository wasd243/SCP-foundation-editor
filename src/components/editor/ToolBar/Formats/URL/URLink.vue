<script setup lang="ts">
import URLink from "../../../../../assets/icons/URLink.svg";

const emit = defineEmits<{
  insert: [];
}>();

function insertLink() {
  emit("insert");
}
</script>

<template>
  <button
    class="format-basic-button url-link"
    type="button"
    aria-label="Insert link"
    @click="insertLink"
  >
    <img :src="URLink" alt="URLink" />
  </button>
</template>
