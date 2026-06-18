import { invoke } from "@tauri-apps/api/core";
import { scanDOMandReplace } from "./htmlAdapter";
import { connectCSSAdapter } from "../../Themes/cssAdapter.ts";

type CodeViewMessage = {
    type: "code-view-content-changed";
    payload: string;
};

type ParseOutput = {
    html: string;
    ast_json: string;
};

const NO_USER_CSS = "/* NO USER CSS */";

/**
 * Injects user CSS into the document.
 * I don't know why this is needed, but it's necessary.
 * The parser has blocked the user CSS for no reason.
 * It seems like there's no issue in `ftml` source code, but the bug is still there.
 * So this ugly hack is the only way I find to fix it.
 *
 * ---
 *
 * Do not remove this function unless you know what happened in the parser and fix it.
 * Or you'll lose your user CSS.
 */
export function patch_injectUserCss(css: string) {
    if (!css.trim() || css.trim() === NO_USER_CSS) return;

    // To force cover ProseMirror styles, we need to add !important to every selector.
    // When exporting, remove those unused !important.
    const forced = css.replace(/(?<! !important);(\s*)$/gm, " !important;$1");

    let styleEl = document.getElementById(
        "user-css-injected",
    ) as HTMLStyleElement | null;
    if (!styleEl) {
        styleEl = document.createElement("style");
        styleEl.id = "user-css-injected";
        document.head.appendChild(styleEl);
    }
    styleEl.textContent = forced;
}

export function setCodeViewIframe(_iframe: HTMLIFrameElement | null) {}

export function SyncToParser() {
    window.addEventListener(
        "message",
        async (event: MessageEvent<CodeViewMessage>) => {
            if (event.data?.type !== "code-view-content-changed") return;

            try {
                const output = await invoke<ParseOutput>("parse_wikidot", {
                    sourceText: event.data.payload,
                });

                if (typeof output.html !== "string") {
                    throw new Error("Parser returned malformed HTML output.");
                }

                try {
                    const css = await invoke<string>("patch_get_user_css");
                    patch_injectUserCss(css);
                } catch {
                    console.warn("No user CSS cache found.");
                }

                await connectCSSAdapter();

                window.dispatchEvent(
                    new CustomEvent("code-view-parser-html", {
                        detail: scanDOMandReplace(output.html),
                    }),
                );

                // The parser writes the module-rate status to a temp file on
                // every parse. Notify listeners so they can refresh from it.
                window.dispatchEvent(new CustomEvent("module-rate-status-changed"));
            } catch (error) {
                window.dispatchEvent(
                    new CustomEvent("code-view-parser-error", {
                        detail:
                            error instanceof Error
                                ? error.message
                                : "Failed to parse code-view content.",
                    }),
                );
            }
        },
    );
}
