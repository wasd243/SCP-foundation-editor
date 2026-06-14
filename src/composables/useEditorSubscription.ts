import { onMounted, onUnmounted } from "vue";
import { getEditor } from "../stores/editor.ts";

const editorReadyPollMs = 100;

/**
 * Runs `sync` when the TipTap editor becomes available, then on selection and document updates.
 */
export function useEditorSubscription(sync: () => void) {
    let stopWatching: (() => void) | null = null;
    let watchTimer: number | null = null;

    function attach() {
        const editor = getEditor();

        if (!editor) {
            return false;
        }

        sync();
        editor.on("selectionUpdate", sync);
        editor.on("transaction", sync);

        stopWatching = () => {
            editor.off("selectionUpdate", sync);
            editor.off("transaction", sync);
        };

        return true;
    }

    onMounted(() => {
        if (attach()) {
            return;
        }

        watchTimer = window.setInterval(() => {
            if (!attach() || watchTimer === null) {
                return;
            }

            window.clearInterval(watchTimer);
            watchTimer = null;
        }, editorReadyPollMs);
    });

    onUnmounted(() => {
        stopWatching?.();

        if (watchTimer !== null) {
            window.clearInterval(watchTimer);
        }
    });
}
