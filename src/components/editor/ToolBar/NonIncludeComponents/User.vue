<script setup lang="ts">
import User from "../../../../assets/icons/User.svg";
import { promptInsertEditorUser } from "../../../../stores/btnToolBar/btnNonIncludeComponents/btnUser.ts";
</script>

<template>
    <button
        class="component-card"
        type="button"
        @click="promptInsertEditorUser"
    >
        <img :src="User" alt="User" />
        User
    </button>
</template>
