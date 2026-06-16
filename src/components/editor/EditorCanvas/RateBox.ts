import { invoke } from "@tauri-apps/api/core";
import { computed, ref } from "vue";

export type RateAlignment = "left" | "center" | "right";

// Mirrors .rate { width: 80px } in EditorCanvasFakeWikidotDivDefaultStyle.sass
const RATE_WIDTH_PX = 80;

export const rateAlignment = ref<RateAlignment>("left");

export const rateBoxStyle = computed<Record<string, string>>(() => {
    switch (rateAlignment.value) {
        case "left":
            return { left: "500px", right: "auto", pointerEvents: "auto" };
        case "center":
            return {
                left: `calc(50% - ${RATE_WIDTH_PX / 2}px)`,
                right: "auto",
                pointerEvents: "auto",
            };
        case "right":
            return { left: "auto", right: "500px", pointerEvents: "auto" };
    }
});

/**
 * Set the default rate-box alignment from the parser's module-rate temp file
 * content (`MODULE_RATE=...\nALIGNMENTS=LEFT|CENTER|RIGHT|NONE`).
 * `NONE` (no explicit alignment context around `[[module rate]]`) falls back
 * to `right`.
 */
export function applyModuleRateAlignment(status: string): void {
    const value = /ALIGNMENTS=(\w+)/i.exec(status)?.[1]?.toUpperCase();

    switch (value) {
        case "LEFT":
            rateAlignment.value = "left";
            break;
        case "CENTER":
            rateAlignment.value = "center";
            break;
        case "RIGHT":
        case "NONE":
        default:
            rateAlignment.value = "right";
            break;
    }
}

/**
 * Write the current rate-box alignment back to the module-rate temp file,
 * preserving the existing MODULE_RATE status line. Called on each moveable
 * position change so the temp file reflects the box's latest alignment.
 */
export async function writeRateAlignmentToTemp(): Promise<void> {
    let status = "MODULE_RATE=FALSE";
    try {
        const current = await invoke<string>("read_module_rate_temp");
        status = /MODULE_RATE=\w+/i.exec(current)?.[0] ?? status;
    } catch {
        // No temp file yet; fall back to the default status.
    }

    const alignment = `ALIGNMENTS=${rateAlignment.value.toUpperCase()}`;

    try {
        await invoke("rewrite_module_rate_temp", { status, alignment });
    } catch (error) {
        console.warn("Failed to write rate alignment to temp.", error);
    }
}

export function getRateDropAlignment(
    containerEl: HTMLElement,
    targetEl: HTMLElement,
): RateAlignment {
    const containerRect = containerEl.getBoundingClientRect();
    const targetRect = targetEl.getBoundingClientRect();
    const elementCenter =
        targetRect.left + targetRect.width / 2 - containerRect.left;
    const third = containerRect.width / 3;

    if (elementCenter < third) return "left";
    if (elementCenter > third * 2) return "right";
    return "center";
}
