<script setup lang="ts">
import { computed, ref } from "vue";
import { useEditorSubscription } from "../../../../../composables/useEditorSubscription.ts";
import { getEditor } from "../../../../../stores/editor.ts";

const currentUrl = ref("");
const hasUrl = computed(() => currentUrl.value.length > 0);

function renderCurrentUrl() {
    const editor = getEditor();

    if (!editor?.isActive("link")) {
        currentUrl.value = "";
        return;
    }

    const href = editor.getAttributes("link").href;
    currentUrl.value = typeof href === "string" ? href : "";
}

useEditorSubscription(renderCurrentUrl);
</script>

<template>
    <div
        class="format-url-preview"
        :class="{ 'is-empty': !hasUrl }"
        :title="currentUrl"
        aria-live="polite"
    >
        {{ hasUrl ? currentUrl : "" }}
    </div>
</template>
