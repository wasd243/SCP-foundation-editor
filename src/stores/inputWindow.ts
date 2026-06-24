import { reactive } from "vue";

// macOS bundled Tauri (WKWebView) does not implement `window.prompt()`, so the
// native call silently returns null and no dialog appears. This store backs a
// custom in-app modal (`InputWindow.vue`) and exposes a promise-based
// `promptInput()` that preserves the same `null`-means-cancel contract as the
// native prompt.

export interface InputWindowOptions {
    title?: string; // dialog heading, e.g. "Insert link"
    label?: string; // field label, e.g. "URL"
    placeholder?: string; // input placeholder example
    defaultValue?: string; // prefill (e.g. current link href)
    confirmText?: string; // primary button text, e.g. "Insert"
}

interface InputWindowState extends Required<InputWindowOptions> {
    visible: boolean;
}

export const inputWindowState = reactive<InputWindowState>({
    visible: false,
    title: "Enter value",
    label: "",
    placeholder: "",
    defaultValue: "",
    confirmText: "OK",
});

let resolver: ((value: string | null) => void) | null = null;

// Opens the modal and resolves to the entered value, or null on cancel.
export function promptInput(
    options: InputWindowOptions = {},
): Promise<string | null> {
    // If a previous prompt is somehow still pending, cancel it so its promise
    // never dangles.
    if (resolver) {
        const previous = resolver;
        resolver = null;
        previous(null);
    }

    inputWindowState.title = options.title ?? "Enter value";
    inputWindowState.label = options.label ?? "";
    inputWindowState.placeholder = options.placeholder ?? "";
    inputWindowState.defaultValue = options.defaultValue ?? "";
    inputWindowState.confirmText = options.confirmText ?? "OK";
    inputWindowState.visible = true;

    return new Promise<string | null>((resolve) => {
        resolver = resolve;
    });
}

// Called by InputWindow.vue to close the modal and settle the pending promise.
export function resolveInputWindow(value: string | null) {
    inputWindowState.visible = false;

    if (resolver) {
        const resolve = resolver;
        resolver = null;
        resolve(value);
    }
}
