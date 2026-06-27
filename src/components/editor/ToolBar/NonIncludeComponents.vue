<script setup lang="ts">
import Code from "./NonIncludeComponents/Code.vue";
import Footnotes from "./NonIncludeComponents/Footnotes.vue";
import Note from "./NonIncludeComponents/Note.vue";
import TabView from "./NonIncludeComponents/TabView.vue";
import User from "./NonIncludeComponents/User.vue";
</script>

<template>
    <div class="component-gallery">
        <TabView />
        <Footnotes />
        <Code />
        <Note />
        <User />
    </div>
</template>
