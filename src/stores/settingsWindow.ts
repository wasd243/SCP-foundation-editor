import { ref } from "vue";

/**
 * Settings-window store.
 *
 * Shared reactive state for the Word "Options"-style settings modal. Mirrors the
 * `updater.ts` / `inputWindow.ts` ref-module convention: plain refs plus a couple
 * of helpers, with the Vue components (`settings/Settings.vue`, the Actions gear
 * button) staying thin and only binding to / calling into these.
 */

export type SettingsCategory = "save" | "display" | "advanced" | "updates";

/** Whether the settings modal is open. */
export const settingsOpen = ref(false);

/** Which category the right-hand pane is showing. */
export const activeCategory = ref<SettingsCategory>("save");

/** Open the modal, optionally jumping straight to a category. */
export function openSettings(category: SettingsCategory = "save"): void {
    activeCategory.value = category;
    settingsOpen.value = true;
}

/** Close the modal. */
export function closeSettings(): void {
    settingsOpen.value = false;
}
