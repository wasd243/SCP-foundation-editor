<script setup lang="ts">
import InsertDiv from "../../../../assets/icons/InsertDiv.svg";
import { ref } from 'vue';
import DivPanel from './DivPanel.vue';
const showDivPanel = ref(false);
</script>

<template>
  <button class="format-insertion-button div-button" type="button" @click="showDivPanel = true">
    <img :src="InsertDiv" alt="Insert Div"/>
    <br>
    div
  </button>
  <DivPanel v-if="showDivPanel" @close="showDivPanel = false"/>
</template>
