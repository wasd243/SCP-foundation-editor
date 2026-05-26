<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import Moveable from "vue3-moveable";
import { editorExtensions, getEditor, setEditor } from "../../stores/editor.ts";
import { getContextMenuFlags, type ContextMenuFlags } from "../../stores/editor/contextMenuFlags.ts";
import { alertNoteExternalParserMarkers } from "../../stores/editor/noteExternalParserGuard.ts";
import { selectedImageBlockElement } from "../../stores/editor/extensions/ImageE.ts";
import ContextMenu from "./ContextMenu.vue";

const contextMenuVisible = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuKey = ref(0);
const contextMenuFlags = ref<ContextMenuFlags>({ showTabView: false, showTable: false });
const imageAlignmentClasses = ["alignleft", "alignright", "aligncenter"];
let captionAlignmentWatchdogId: ReturnType<typeof window.setInterval> | null = null;
const selectedImageResizable = computed(() =>
    selectedImageBlockElement.value?.getAttribute("data-editor-no-resize") !== "true"
);

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

function findImageContainerParent(element: HTMLElement) {
  let parent = element.parentElement;

  while (parent) {
    if (parent.tagName.toLowerCase() === "div" && parent.classList.contains("image-container")) {
      return parent;
    }

    parent = parent.parentElement;
  }

  return null;
}

function getImageContainerTarget(element: HTMLElement) {
  if (element.tagName.toLowerCase() === "div" && element.classList.contains("image-container")) {
    return element;
  }

  return findImageContainerParent(element);
}

function findNodePositionByElement(element: HTMLElement) {
  const editorInstance = getEditor();

  if (!editorInstance) {
    return null;
  }

  let position: number | null = null;

  editorInstance.state.doc.descendants((_node, pos) => {
    if (editorInstance.view.nodeDOM(pos) === element) {
      position = pos;
      return false;
    }

    return true;
  });

  return position;
}

function setSizeStyle(styleText: unknown, width: string, height: string) {
  const element = document.createElement("div");

  element.style.cssText = typeof styleText === "string" ? styleText : "";
  element.style.width = width;
  element.style.height = height;

  return element.style.cssText;
}

function updateImageContainerNodeStyle(container: HTMLElement, width: string, height: string) {
  const editorInstance = getEditor();
  const position = findNodePositionByElement(container);

  if (!editorInstance || position === null) {
    return;
  }

  const node = editorInstance.state.doc.nodeAt(position);

  if (!node || !node.attrs.htmlAttributes || typeof node.attrs.htmlAttributes !== "object") {
    return;
  }

  const htmlAttributes = node.attrs.htmlAttributes as Record<string, unknown>;

  editorInstance.view.dispatch(
      editorInstance.state.tr.setNodeMarkup(position, undefined, {
        ...node.attrs,
        htmlAttributes: {
          ...htmlAttributes,
          style: setSizeStyle(htmlAttributes.style, width, height),
        },
      }, node.marks)
  );
}

function syncImageContainerSize(container: HTMLElement, width: string, height: string) {
  const img = container.querySelector("img") as HTMLElement | null;

  container.style.width = width;
  container.style.height = height;

  if (!img) {
    return;
  }

  img.style.width = width;
  img.style.height = height;
}

function setEditorDomObserverEnabled(enabled: boolean) {
  const editorInstance = getEditor();
  //@ts-ignore
  const domObserver = editorInstance?.view.domObserver as {
    start?: () => void;
    stop?: () => void;
  } | undefined;

  if (enabled) {
    domObserver?.start?.();
  } else {
    domObserver?.stop?.();
  }
}

function onImageResizeStart() {
  setEditorDomObserverEnabled(false);
}

function onImageResize(e: any) {
  const target = e.target as HTMLElement;
  const width = `${e.width}px`;
  const height = `${e.height}px`;
  const container = getImageContainerTarget(target);

  if (container) {
    syncImageContainerSize(container, width, height);
    return;
  }

  target.style.width = width;
  target.style.height = height;
}

function onImageResizeEnd(e: any) {
  const width = `${Math.round(e.lastEvent?.width ?? e.target.offsetWidth)}px`;
  const height = `${Math.round(e.lastEvent?.height ?? e.target.offsetHeight)}px`;
  const target = e.target as HTMLElement;
  const container = getImageContainerTarget(target);

  if (container) {
    syncImageContainerSize(container, width, height);
    updateImageContainerNodeStyle(container, width, height);
    setEditorDomObserverEnabled(true);
    return;
  }

  target.style.width = width;
  target.style.height = height;
  setEditorDomObserverEnabled(true);
}

onMounted(() => {
  window.addEventListener("pointerdown", closeContextMenuOnPointerDown, true);
  captionAlignmentWatchdogId = window.setInterval(() => {
    const root = getEditor()?.view.dom;

    if (!root) {
      return;
    }

    root.querySelectorAll(".scp-image-caption").forEach(caption => {
      if (!(caption instanceof HTMLElement)) {
        return;
      }

      if (imageAlignmentClasses.some(className => caption.classList.contains(className))) {
        return;
      }

      const imageContainer = findImageContainerParent(caption);
      const alignClass = imageContainer
          ? imageAlignmentClasses.find(className => imageContainer.classList.contains(className))
          : null;

      if (alignClass) {
        caption.classList.add(alignClass);
      }
    });

    root.querySelectorAll("div.image-container").forEach(container => {
      if (!(container instanceof HTMLElement)) {
        return;
      }

      const noResizePlainAlignedImage =
          imageAlignmentClasses.some(className => container.classList.contains(className)) &&
          !container.hasAttribute("data-editor-include");

      if (noResizePlainAlignedImage) {
        container.setAttribute("data-editor-no-resize", "true");
      } else {
        container.removeAttribute("data-editor-no-resize");
      }
    });
  }, 1000);
});

onUnmounted(() => {
  window.removeEventListener("pointerdown", closeContextMenuOnPointerDown, true);
  if (captionAlignmentWatchdogId !== null) {
    window.clearInterval(captionAlignmentWatchdogId);
    captionAlignmentWatchdogId = null;
  }
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

    <Moveable
        :target="selectedImageBlockElement || undefined"
        :resizable="selectedImageResizable"
        :draggable="false"
        :keepRatio="false"
        :renderDirections="['nw', 'ne', 'sw', 'se', 'n', 'w', 's', 'e']"
        @resizeStart="onImageResizeStart"
        @resize="onImageResize"
        @resizeEnd="onImageResizeEnd"
    />
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
  position: relative;
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
