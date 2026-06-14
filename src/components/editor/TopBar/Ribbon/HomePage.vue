<!--HomePage.vue is used to display the toolbar rather than components-->

<script setup lang="ts">
import Formats from "../../ToolBar/Formats.vue";
import CodeView from "../../ToolBar/CodeView.vue";
import NonIncludeComponents from "../../ToolBar/NonIncludeComponents.vue";
</script>
<template>
    <div class="ribbon-layout" data-ribbon-page="home">
        <Formats />
        <CodeView />
        <NonIncludeComponents />
        <div class="ribbon-separator"></div>
        <div class="ribbon-separator small-1"></div>

        <!--This div is waiting for future implementation-->
        <!--<div class="ribbon-separator small-2"></div>-->

        <div class="ribbon-separator normal-1"></div>
        <div class="ribbon-separator normal-2"></div>
    </div>
</template>
