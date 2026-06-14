<script setup lang="ts">
import URLSite from "../../../../../assets/icons/URLSite.svg";

const emit = defineEmits<{
    insert: [];
}>();

function insertSiteLink() {
    emit("insert");
}
</script>

<template>
    <button
        class="format-basic-button url-site"
        type="button"
        aria-label="Insert site link"
        @click="insertSiteLink"
    >
        <img :src="URLSite" alt="URL Site" />
        Site
    </button>
</template>
