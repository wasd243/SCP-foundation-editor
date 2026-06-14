<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import { editorExtensions, getEditor, setEditor } from "../../stores/editor.ts";
import {
    getContextMenuFlags,
    type ContextMenuFlags,
} from "../../stores/editor/contextMenuFlags.ts";
import { alertNoteExternalParserMarkers } from "../../stores/editor/noteExternalParserGuard.ts";
import { selectedImageBlockElement } from "../../stores/editor/extensions/ImageE.ts";
import { SyncJSONToExporter } from "../../ipc/Extensions/CodeExport/getJSON.ts";
import ContextMenu from "./ContextMenu.vue";
import EditorCanvasMoveable from "./EditorCanvas/Moveable.vue";

const contextMenuVisible = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuKey = ref(0);
const contextMenuFlags = ref<ContextMenuFlags>({
    showTabView: false,
    showTable: false,
    showImage: false,
});

function handleContextMenu(event: MouseEvent) {
    if (!(event.target instanceof Element)) {
        return;
    }

    if (event.target.closest(".editor-context-menu")) {
        return;
    }

    event.preventDefault();
    event.stopPropagation();

    const imageContainer = getImageContainerTarget(event.target as HTMLElement);

    if (imageContainer && !imageContainer.hasAttribute("data-editor-include")) {
        selectedImageBlockElement.value = imageContainer;
    }

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
                editorInstance
                    .chain()
                    .focus()
                    .setTextSelection(position.pos)
                    .run();
            } catch {
                // Keep the context menu available even when ProseMirror rejects an edge position.
            }
        }
    }

    if (editorInstance) {
        contextMenuFlags.value = getContextMenuFlags(
            editorInstance,
            clickPos,
            event.target,
        );
    } else {
        contextMenuFlags.value = {
            showTabView: false,
            showTable: false,
            showImage: false,
        };
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

    if (
        event.target instanceof Element &&
        event.target.closest(".editor-context-menu")
    ) {
        return;
    }

    contextMenuVisible.value = false;
}

function findImageContainerParent(element: HTMLElement) {
    let parent = element.parentElement;

    while (parent) {
        if (
            parent.tagName.toLowerCase() === "div" &&
            parent.classList.contains("image-container")
        ) {
            return parent;
        }

        parent = parent.parentElement;
    }

    return null;
}

function getImageContainerTarget(element: HTMLElement) {
    if (
        element.tagName.toLowerCase() === "div" &&
        element.classList.contains("image-container")
    ) {
        return element;
    }

    return findImageContainerParent(element);
}

onMounted(() => {
    window.addEventListener("pointerdown", closeContextMenuOnPointerDown, true);
});

onUnmounted(() => {
    window.removeEventListener(
        "pointerdown",
        closeContextMenuOnPointerDown,
        true,
    );
});

const editor = useEditor({
    extensions: editorExtensions,
    content: "<p>Hello FTML editor.</p>",

    onCreate: ({ editor }) => {
        setEditor(editor);
        alertNoteExternalParserMarkers(editor);
        SyncJSONToExporter();
    },
    onUpdate: ({ editor }) => {
        alertNoteExternalParserMarkers(editor);
        SyncJSONToExporter();
    },
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

            view.dispatch(view.state.tr.insertText(text));

            return true;
        },
    },
});
</script>

<template>
    <main class="editor-canvas editor-theme-default">
        <!--These div are here to support wiki css themes-->
        <!--I DO NOT promise that these would support all legacy wikidot css-->
        <!--GOOD LUCK-->
        <div id="container-wrap">
            <div id="header">
                <h1>
                    <span>Editor Header</span>
                </h1>
            </div>
            <div id="top-bar">Editor Top Bar</div>

            <div class="meta-title">Editor Meta Title Preview</div>

            <div id="side-bar">Editor side-bar</div>
        </div>

        <EditorContent :editor="editor" />
        <EditorCanvasMoveable />
    </main>

    <Teleport to="body">
        <ContextMenu
            v-if="contextMenuVisible"
            :key="contextMenuKey"
            :x="contextMenuX"
            :y="contextMenuY"
            :show-tab-view="contextMenuFlags.showTabView"
            :show-table="contextMenuFlags.showTable"
            :show-image="contextMenuFlags.showImage"
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
    top: min(200px);

    background: #ffffff;

    outline: none;
}

:deep(.ProseMirror:focus) {
    outline: none;
}
</style>
