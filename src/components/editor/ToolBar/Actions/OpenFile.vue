<script setup lang="ts">
import Open2 from "../../../../assets/icons/Open2.svg";
import {OpenFtml} from "../../../../stores/btnToolBar/btnActions/btnOpenFile.ts";
</script>

<template>
  <button class="actions-button open-file" type="button" @click="OpenFtml">
    <img :src="Open2" alt="Open"/>
    Open
  </button>
</template>
