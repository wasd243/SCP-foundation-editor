<script setup lang="ts">
const codeViewUrl = "/code_view/index.html";

function openCodeView() {
  window.open(codeViewUrl, "_blank", "noopener,noreferrer");
}
</script>

<!--Use basic.css style for code view button-->
<template>
  <button class="code-view" type="button" @click="openCodeView">&lt;/&gt;</button>
  <iframe class="code-view-frame" :src="codeViewUrl" title="Code view"></iframe>
</template>
