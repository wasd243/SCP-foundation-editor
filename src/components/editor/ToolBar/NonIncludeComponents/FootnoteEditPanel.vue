<script setup lang="ts"></script>

<template>
    <div class="footnote-edit-panel">
        <h1>Footnotes</h1>
        <div class="wj-footnote-list"></div>
    </div>
</template>

<style scoped lang="sass">
// Variables - One Dark Theme Colors
$bg-base: #1e1e1e
$bg-editor: #282c34
$bg-scrollbar-track: #21252b
$bg-scrollbar-thumb: #4b5363
$bg-scrollbar-thumb-hover: #5c6370
$border-color: #181a1f
$text-main: #abb2bf

.footnote-edit-panel
    width: 20vw
    height: 100vh
    background-color: $bg-editor
    color: $text-main
    overflow-y: auto
    box-sizing: border-box
    padding: 30px
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace
    font-size: 15px
    line-height: 1.6
    box-shadow: -5px 0 20px rgba(0, 0, 0, 0.4)
    display: flex
    position: fixed
    right: 60px
    top: 380px
    z-index: 9999 // high z-index to make sure user can see it

    // Custom Scrollbar
    &::-webkit-scrollbar
        width: 14px

    &::-webkit-scrollbar-track
        background: $bg-scrollbar-track
        border-left: 1px solid $border-color

    &::-webkit-scrollbar-thumb
        background: $bg-scrollbar-thumb
        border: 3px solid $bg-scrollbar-track
        border-radius: 8px

        &:hover
            background: $bg-scrollbar-thumb-hover
</style>
