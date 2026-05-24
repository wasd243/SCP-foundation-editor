<script setup lang="ts">
import Note from "../../../../assets/icons/Note.svg";
import { insertEditorNote } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnNote.ts";
</script>

<template>
  <button class="component-card" type="button" @click="insertEditorNote">
    <img :src="Note" alt="Note"/>
    Note
  </button>
</template>
