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
import { signalMainReady } from "../../splashscreen.ts";
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
    content: `<p><em>web
    DEMO功能不全，只是想给各位试试手感，代码生成/图片插入/自定义CSS/DIV等功能均在本地版。</em><br><strong>这是一行加粗文本</strong><br><em><strong>这是一行斜体</strong></em><br><u><em><strong>这是一行下划线</strong></em></u><br><s><u><em><strong>再加上删除线</strong></em></u></s><br>和各种<sup>角</sup><sub>标</sub>还有
</p>
<blockquote><p>引用</p></blockquote>
<table class="wiki-content-table">
    <tbody>
    <tr>
        <th>表格</th>
        <th>表格</th>
    </tr>
    <tr>
        <td>表格</td>
        <td>表格</td>
    </tr>
    </tbody>
</table>
<div style="text-align: right;"><p>对齐</p></div>
<div style="text-align: left;">
    <p><a href="https://github.com">链接</a>点那个扫把就能清除样式，包括链接<br>站内链接只是生成格式不一样
        <footnote>脚注编辑器，点一下就能打开</footnote>
        ，比如：<a class="active" href="/scp-173">花生</a></p>
</div>
<wj-tabs class="wj-tabs">
    <div class="wj-tabs-button-list" role="tablist">
        <wj-tabs-button aria-controls="wj-id-90iorOM6Psbdo4nX" aria-label="Tab 1" aria-selected="true"
                        class="wj-tabs-button" id="wj-id-BKmrs54aJBrcFzpC" role="tab" tabindex="0">Tab 1
        </wj-tabs-button>
        <wj-tabs-button aria-controls="wj-id-j4s8681iQXjmV2ur" aria-label="Tab 2" aria-selected="false"
                        class="wj-tabs-button" id="wj-id-IU3yipKBDbjDXU2k" role="tab" tabindex="-1">Tab 2
        </wj-tabs-button>
    </div>
    <div class="wj-tabs-panel-list">
        <div aria-labelledby="wj-id-BKmrs54aJBrcFzpC" class="wj-tabs-panel" id="wj-id-90iorOM6Psbdo4nX" role="tabpanel"
             tabindex="0"><p>tabview</p></div>
        <div aria-labelledby="wj-id-IU3yipKBDbjDXU2k" class="wj-tabs-panel" hidden="" id="wj-id-j4s8681iQXjmV2ur"
             role="tabpanel" tabindex="0"><p><span style="white-space: pre-wrap;"></span></p></div>
    </div>
</wj-tabs>
<details class="wj-collapsible" data-show-top="">
    <summary class="wj-collapsible-button wj-collapsible-button-top"><span class="wj-collapsible-show-text">+生成折叠块的时候记得放上加减号</span><span
        class="wj-collapsible-hide-text">-生成折叠块的时候记得放上加减号</span></summary>
    <div class="wj-collapsible-content"><p>左边这个灰条是提示文本再折叠块内的</p>
        <p>折叠块内啥都能放</p>
        <wj-tabs class="wj-tabs">
            <div class="wj-tabs-button-list" role="tablist">
                <wj-tabs-button aria-controls="wj-id-TeQUS4gqi0Dmpnvh" aria-label="Tab 1" aria-selected="true"
                                class="wj-tabs-button" id="wj-id-LagIkYqB1gENDat3" role="tab" tabindex="0">Tab 1
                </wj-tabs-button>
            </div>
            <div class="wj-tabs-panel-list">
                <div aria-labelledby="wj-id-LagIkYqB1gENDat3" class="wj-tabs-panel" id="wj-id-TeQUS4gqi0Dmpnvh"
                     role="tabpanel" tabindex="0"><p>比如tabview</p></div>
            </div>
        </wj-tabs>
    </div>
</details>
<div class="wj-note"><p>笔记模块</p>
    <p>和分割线</p></div>
<hr><p>字体<span style="color: #D81B43;">颜色</span>设置点<span style="color: #D81B43;">A</span>再点对应颜色，生成的维基代码默认为十六进制颜色格式。
</p>`,

    onCreate: ({ editor }) => {
        setEditor(editor);
        attachActiveFormats(editor);
        alertNoteExternalParserMarkers(editor);
        SyncJSONToExporter();

        // Editor is mounted and ready — signal the splash so it can start its
        // 5s auto-close countdown anchored to this readiness moment.
        //
        // Call directly, NOT via requestAnimationFrame: the main window starts
        // hidden (tauri.conf.json `visible: false`), and on macOS a hidden
        // WebView's display-link is suspended, so an rAF callback would never
        // fire — leaving the splash stuck on "Initializing editor…" forever.
        signalMainReady();
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
