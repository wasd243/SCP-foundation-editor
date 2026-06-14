<script setup lang="ts">
import Copy from "./DefaultContextMenu/Copy.vue";
import InsertFootnote from "./DefaultContextMenu/InsertFootnote.vue";
import Paste from "./DefaultContextMenu/Paste.vue";
</script>

<template>
    <div class="context-menu-section">
        <Copy />
        <Paste />
        <div class="context-menu-separator"></div>
        <InsertFootnote />
    </div>
</template>
