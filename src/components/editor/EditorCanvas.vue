<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import VueMoveable from "vue3-moveable";
import { editorExtensions, getEditor, setEditor } from "../../stores/editor.ts";
import { attachActiveFormats } from "../../stores/btnToolBar/activeFormats.ts";
import { invoke } from "@tauri-apps/api/core";
import {
    rateAlignment,
    rateBoxStyle,
    getRateDropAlignment,
    applyModuleRateAlignment,
    applyModuleRateVisibility,
    writeRateAlignmentToTemp,
    rateVisible,
} from "./EditorCanvas/RateBox.ts";
import {
    getContextMenuFlags,
    type ContextMenuFlags,
} from "../../stores/editor/contextMenuFlags.ts";
import { alertNoteExternalParserMarkers } from "../../stores/editor/noteExternalParserGuard.ts";
import { selectedImageBlockElement } from "../../stores/editor/extensions/ImageE.ts";
import { SyncJSONToExporter } from "../../ipc/Extensions/CodeExport/getJSON.ts";
import { closeSplashscreen } from "../../splashscreen.ts";
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

/**
 * Refresh the default rate-box alignment from the parser's module-rate temp
 * file, which is rewritten on every `parse_wikidot` call.
 */
async function refreshRateAlignment() {
    try {
        const status = await invoke<string>("read_module_rate_temp");
        applyModuleRateAlignment(status);
        applyModuleRateVisibility(status);
    } catch (error) {
        console.warn("Failed to read module-rate alignment.", error);
    }
}

onMounted(() => {
    window.addEventListener("pointerdown", closeContextMenuOnPointerDown, true);
    window.addEventListener("module-rate-status-changed", refreshRateAlignment);

    // Initialize alignment/visibility from temp on first mount.
    refreshRateAlignment();
});

onUnmounted(() => {
    window.removeEventListener(
        "pointerdown",
        closeContextMenuOnPointerDown,
        true,
    );
    window.removeEventListener(
        "module-rate-status-changed",
        refreshRateAlignment,
    );
});

const rateButtonRef = ref<HTMLElement | null>(null);

function onRateDrag(e: any) {
    (e.target as HTMLElement).style.transform = e.transform;
}

function onRateDragEnd(e: any) {
    const target = e.target as HTMLElement;
    const containerEl = document.querySelector<HTMLElement>("#container-wrap");

    if (!containerEl) {
        target.style.transform = "";
        return;
    }

    const alignment = getRateDropAlignment(containerEl, target);
    target.style.transform = "";
    rateAlignment.value = alignment;
    writeRateAlignmentToTemp();
}

const editor = useEditor({
    extensions: editorExtensions,
    content: "<p>Hello FTML editor.</p>",

    onCreate: ({ editor }) => {
        setEditor(editor);
        attachActiveFormats(editor);
        alertNoteExternalParserMarkers(editor);
        SyncJSONToExporter();

        // Editor is mounted and ready — dismiss the splash on the next frame
        // so the main window appears already painted, not blank.
        requestAnimationFrame(() => closeSplashscreen());
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
        <!--GOOD LUCK-->
        <div id="container-wrap">
            <!--ARCHIVED: TO SEE FULL EXPLANATION, GO TO not-planned/theme ROOT DIRECTORY README.md.bak-->
            <div id="content-wrap">
                <button ref="rateButtonRef" class="rate" :style="rateBoxStyle">
                    Rate: + - x
                </button>
            </div>
        </div>

        <EditorContent :editor="editor" />
        <EditorCanvasMoveable />
        <VueMoveable
            v-if="rateVisible"
            :target="rateButtonRef || undefined"
            :draggable="true"
            :resizable="false"
            @drag="onRateDrag"
            @dragEnd="onRateDragEnd"
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
    top: 0;

    background: #ffffff;

    outline: none;
}

:deep(.ProseMirror:focus) {
    outline: none;
}
</style>
