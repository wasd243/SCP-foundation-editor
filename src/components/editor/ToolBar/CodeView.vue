<script setup lang="ts">
import {invoke} from "@tauri-apps/api/core";
import {onBeforeUnmount, ref, watch} from "vue";
import RenderSyncHtmlToEditor from "./CodeView/RenderSyncHTMLToEditor.vue";
import {setCodeViewIframe} from "../../../ipc/Extensions/CodeView/SyncToParser";

const isCodeViewOpen = ref(false);
const isCodeViewOpening = ref(false);
const codeViewOpenError = ref("");
const codeViewSrc = ref("");
const codeViewIframe = ref<HTMLIFrameElement | null>(null);

defineExpose({});

watch(codeViewIframe, iframe => {
  setCodeViewIframe(iframe);
});

onBeforeUnmount(() => {
  setCodeViewIframe(null);
});

function formatOpenError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return "Failed to open code view. Try again.";
}

async function openCodeView() {
  if (isCodeViewOpening.value || isCodeViewOpen.value) {
    return;
  }

  isCodeViewOpening.value = true;
  codeViewOpenError.value = "";

  try {
    codeViewSrc.value = await invoke<string>("open_code_view_window");
    isCodeViewOpen.value = true;
  } catch (error) {
    codeViewOpenError.value = formatOpenError(error);
    console.error("[CodeView] open_code_view_window failed:", error);
  } finally {
    isCodeViewOpening.value = false;
  }
}

function closeCodeView() {
  isCodeViewOpen.value = false;
  codeViewOpenError.value = "";
}
</script>

<template>
  <div class="code-view-controls">
    <button
        class="code-view"
        type="button"
        :disabled="isCodeViewOpening || isCodeViewOpen"
        :aria-busy="isCodeViewOpening"
        aria-label="Open code view"
        @click="openCodeView"
    >
      <span v-if="isCodeViewOpening" class="code-view-loading" aria-hidden="true">…</span>
      <span v-else>&lt;/&gt;</span>
    </button>
    <p
        v-if="codeViewOpenError"
        class="code-view-error"
        role="alert"
    >
      {{ codeViewOpenError }}
      <button
          class="code-view-retry"
          type="button"
          :disabled="isCodeViewOpening"
          @click="openCodeView"
      >
        Retry
      </button>
    </p>
  </div>
  <RenderSyncHtmlToEditor/>

  <Teleport to="body">
    <Transition name="code-view-slide">
      <section
          v-if="isCodeViewOpen"
          class="code-view-panel"
      >
        <button
            class="code-view-close"
            type="button"
            @click="closeCodeView"
        >
          &times;
        </button>
        <iframe
            ref="codeViewIframe"
            class="code-view-frame"
            :src="codeViewSrc"
            title="Code View"
        ></iframe>
      </section>
    </Transition>
  </Teleport>
</template>

<style scoped>
.code-view-controls {
  position: absolute;
  top: var(--default-code-view-positon);
  left: 10px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.code-view-error {
  margin: 0;
  max-width: 220px;
  padding: 6px 8px;
  border: 1px solid #c53030;
  background: #fff5f5;
  color: #9b2c2c;
  font-family: var(--font-ui), sans-serif;
  font-size: 12px;
  line-height: 1.35;
}

.code-view-retry {
  margin-left: 6px;
  padding: 2px 8px;
  border: 1px solid #c53030;
  background: #ffffff;
  color: #9b2c2c;
  font-size: 12px;
  cursor: pointer;
}

.code-view-retry:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.code-view-loading {
  display: inline-block;
  font-size: 28px;
  line-height: 1;
}

.code-view-panel {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: #282c34;
}

.code-view-frame {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
}

.code-view-close {
  position: absolute;
  top: 60px;
  right: 30px;
  z-index: 1;
  width: 32px;
  height: 32px;
  border: 1px solid #ffffff;
  background: #000000;
  color: #ffffff;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.code-view-slide-enter-active,
.code-view-slide-leave-active {
  transition: transform 180ms ease;
}

.code-view-slide-enter-from,
.code-view-slide-leave-to {
  transform: translateX(-100%);
}
</style>
