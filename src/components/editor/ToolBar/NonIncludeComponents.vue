<script setup lang="ts">
import Code from "./NonIncludeComponents/Code.vue";
import cssModule from "./NonIncludeComponents/cssModule.vue";
import divBlock from "./NonIncludeComponents/divBlock.vue";
import Footnotes from "./NonIncludeComponents/Footnotes.vue";
import ModuleRate from "./NonIncludeComponents/ModuleRate.vue";
import Note from "./NonIncludeComponents/Note.vue";
import TabView from "./NonIncludeComponents/TabView.vue";
import Users from "./NonIncludeComponents/Users.vue";
</script>

<template>
  <div class="component-gallery">
    <TabView/>
    <Footnotes/>
    <Code/>
    <Note/>
    <cssModule/>
    <divBlock/>
    <ModuleRate/>
    <Users/>
  </div>
</template>
