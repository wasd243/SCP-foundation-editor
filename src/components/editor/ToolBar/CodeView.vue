<script setup lang="ts">
import { invoke } from "@tauri-apps/api/core";
import { ref } from "vue";

const isCodeViewOpen = ref(false);
const codeViewSrc = ref("");

defineExpose({});

async function openCodeView() {
  try {
    codeViewSrc.value = await invoke<string>("open_code_view_window");
    isCodeViewOpen.value = true;
  } catch (error) {
    console.error(error);
  }
}

function closeCodeView() {
  isCodeViewOpen.value = false;
}
</script>

<template>
  <button
      class="code-view"
      type="button"
      @click="openCodeView"
  >
    &lt;/&gt;
  </button>

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
            class="code-view-frame"
            :src="codeViewSrc"
            title="Code View"
        ></iframe>
      </section>
    </Transition>
  </Teleport>
</template>

<style scoped>
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
