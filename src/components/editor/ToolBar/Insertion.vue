<script setup lang="ts">
import InsertImage from "./Insertion/InsertImage.vue";
import InsertImageBlock from "./Insertion/InsertImageBlock.vue";
import InsertCSS from "./Insertion/InsertCSS.vue";
import InsertDiv from "./Insertion/InsertDiv.vue";
</script>

<template>
  <InsertImage/>
  <InsertImageBlock/>
  <div class="ribbon-separator insertion-normal-1"></div>
  <InsertCSS/>
  <InsertDiv/>
</template>
