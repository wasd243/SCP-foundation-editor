<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import { editorExtensions, getEditor, setEditor } from "../../stores/editor.ts";
import { getContextMenuFlags, type ContextMenuFlags } from "../../stores/editor/contextMenuFlags.ts";
import { alertNoteExternalParserMarkers } from "../../stores/editor/noteExternalParserGuard.ts";
import ContextMenu from "./ContextMenu.vue";

const contextMenuVisible = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuKey = ref(0);
const contextMenuFlags = ref<ContextMenuFlags>({ showTabView: false, showTable: false });

function handleContextMenu(event: MouseEvent) {
  if (!(event.target instanceof Element)) {
    return;
  }

  if (event.target.closest(".editor-context-menu")) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  const editorInstance = getEditor();
  const position = editorInstance?.view.posAtCoords({
    left: event.clientX,
    top: event.clientY,
  });
  let clickPos: number | null = null;

  if (editorInstance && position && Number.isInteger(position.pos)) {
    const docSize = editorInstance.state.doc.content.size;

    if (position.pos >= 0 && position.pos <= docSize) {
      clickPos = position.pos;

      try {
        editorInstance.chain().focus().setTextSelection(position.pos).run();
      } catch {
        // Keep the context menu available even when ProseMirror rejects an edge position.
      }
    }
  }

  if (editorInstance) {
    contextMenuFlags.value = getContextMenuFlags(editorInstance, clickPos, event.target);
  } else {
    contextMenuFlags.value = { showTabView: false, showTable: false };
  }

  contextMenuKey.value += 1;
  contextMenuX.value = event.clientX;
  contextMenuY.value = event.clientY;
  contextMenuVisible.value = true;
}

function closeContextMenuOnPointerDown(event: PointerEvent) {
  if (!contextMenuVisible.value || event.button !== 0) {
    return;
  }

  if (event.target instanceof Element && event.target.closest(".editor-context-menu")) {
    return;
  }

  contextMenuVisible.value = false;
}

onMounted(() => {
  window.addEventListener("pointerdown", closeContextMenuOnPointerDown, true);
});

onUnmounted(() => {
  window.removeEventListener("pointerdown", closeContextMenuOnPointerDown, true);
});

const editor = useEditor({
  extensions: editorExtensions,
  content: "<p>Hello FTML editor.</p>",

  onCreate: ({ editor }) => {
    setEditor(editor);
    alertNoteExternalParserMarkers(editor);
  },
  onUpdate: ({ editor }) => alertNoteExternalParserMarkers(editor),
  onDestroy: () => setEditor(null),

  editorProps: {
    handleDOMEvents: {
      contextmenu: (_view, event) => {
        handleContextMenu(event);
        return true;
      },
    },
    handlePaste(view, event) {
      const text = event.clipboardData?.getData("text/plain");

      if (!text) {
        return false;
      }

      event.preventDefault();

      view.dispatch(
          view.state.tr.insertText(text)
      );

      return true;
    },
  },
});

</script>

<template>
  <main class="editor-canvas editor-theme-default">
    <EditorContent :editor="editor"/>
  </main>

  <Teleport to="body">
    <ContextMenu
        v-if="contextMenuVisible"
        :key="contextMenuKey"
        :x="contextMenuX"
        :y="contextMenuY"
        :show-tab-view="contextMenuFlags.showTabView"
        :show-table="contextMenuFlags.showTable"
    />
  </Teleport>
</template>

<style scoped>
.editor-canvas {
  height: calc(100vh - var(--topbar-height) - var(--ribbon-height));
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding: 32px 0;
  background: #f2f3f5;
  box-sizing: border-box;
}

:deep(.ProseMirror) {
  width: min(900px, calc(100vw - 96px));
  min-height: 2000px;
  margin: 0 auto;
  padding: 48px 56px;
  box-sizing: border-box;

  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);

  outline: none;
}

:deep(.ProseMirror:focus) {
  outline: none;
}
</style>
