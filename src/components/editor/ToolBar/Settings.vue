<script setup lang="ts">
import AutoSaveSetting from "./Settings/AutoSaveSetting.vue";
import InvisibleCharactersSetting from "./Settings/InvisibleCharactersSetting.vue";
import SavesPathSetting from "./Settings/SavesPathSetting.vue";
import LogAndWriteJson from "./Settings/LogAndWriteJson.vue";
</script>

<template>
    <div class="settings-groups">
        <AutoSaveSetting />
        <div class="settings-groups__divider" aria-hidden="true"></div>
        <InvisibleCharactersSetting />
        <div class="settings-groups__divider" aria-hidden="true"></div>
        <SavesPathSetting />
        <div class="settings-groups__divider" aria-hidden="true"></div>
        <LogAndWriteJson />
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
