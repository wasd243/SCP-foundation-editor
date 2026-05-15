<script setup lang="ts">
import Code from "./NonIncludeComponents/Code.vue";
import cssModule from "./NonIncludeComponents/cssModule.vue";
import divBlock from "./NonIncludeComponents/divBlock.vue";
import Footnotes from "./NonIncludeComponents/Footnotes.vue";
import Image from "./NonIncludeComponents/Image.vue";
import ModuleRate from "./NonIncludeComponents/ModuleRate.vue";
import Note from "./NonIncludeComponents/Note.vue";
import SiteURLs from "./NonIncludeComponents/SiteURLs.vue";
import TabView from "./NonIncludeComponents/TabView.vue";
import URLs from "./NonIncludeComponents/URLs.vue";
import Users from "./NonIncludeComponents/Users.vue";
</script>

<template>
  <div class="component-gallery">
    <TabView/>
    <Footnotes/>
    <Code/>
    <cssModule/>
    <divBlock/>
    <Image/>
    <ModuleRate/>
    <Note/>
    <SiteURLs/>
    <URLs/>
    <Users/>
  </div>
</template>
