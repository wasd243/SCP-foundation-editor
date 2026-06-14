<script setup lang="ts">
import Save2 from "../../../../assets/icons/Save2.svg";
import { SaveFtml } from "../../../../stores/btnToolBar/btnActions/btnSave.ts";
</script>

<template>
    <button class="actions-button save" type="button" @click="SaveFtml">
        <img :src="Save2" alt="Save" />
        Save
    </button>
</template>
