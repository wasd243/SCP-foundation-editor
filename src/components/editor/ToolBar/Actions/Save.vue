<script setup lang="ts">
import Save from "../../../../assets/icons/Save.svg";
import {SaveFtml} from "../../../../stores/btnToolBar/btnActions/btnSave.ts";
</script>

<template>
  <button class="actions-button save" type="button" @click="SaveFtml">
    <img :src="Save" alt="Save"/>
  </button>
</template>
