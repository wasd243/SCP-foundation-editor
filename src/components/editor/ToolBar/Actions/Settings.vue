<script setup lang="ts">
import SettingsIcon from "../../../../assets/icons/Settings.svg";
import { openSettings } from "../../../../stores/settingsWindow.ts";
</script>

<template>
    <button
        class="actions-button settings"
        type="button"
        aria-label="Settings"
        title="Settings"
        @click="openSettings()"
    >
        <img :src="SettingsIcon" alt="Settings" />
    </button>
</template>
