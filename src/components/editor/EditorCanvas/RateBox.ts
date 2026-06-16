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
