<script setup lang="ts">
import InvisibleCharactersSetting from "./Settings/InvisibleCharactersSetting.vue";
</script>

<template>
    <div class="settings-groups">
        <InvisibleCharactersSetting />
        <div class="settings-groups__divider" aria-hidden="true"></div>
    </div>
</template>

<style scoped>
.settings-groups {
    display: flex;
    align-items: stretch;
    gap: 0;
}

.settings-groups__divider {
    width: 1px;
    align-self: stretch;
    margin: 2px 0;
    background: var(--group-border);
}
</style>
