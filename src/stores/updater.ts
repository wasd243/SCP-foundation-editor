import { ref } from "vue";
import { check, type Update } from "@tauri-apps/plugin-updater";
import { relaunch } from "@tauri-apps/plugin-process";
import { getVersion } from "@tauri-apps/api/app";

/**
 * Auto-update store.
 *
 * Shared reactive state + helpers driving the whole update flow:
 * check → release notes → download (with progress) → install → relaunch.
 * The Vue components (UpdateBanner / UpdateDialog / UpdateSetting) stay thin
 * and only bind to / call into these helpers. Mirrors the savesPath store
 * pattern. Every call is wrapped so it is a safe no-op outside Tauri (e.g.
 * plain `npm run dev` in a browser) — a rejected invoke just lands in `error`.
 */

export type UpdateStatus =
    | "idle"
    | "checking"
    | "available"
    | "downloading"
    | "downloaded"
    | "upToDate"
    | "error";

/** Where the flow currently is. Drives every piece of update UI. */
export const status = ref<UpdateStatus>("idle");

/** This build's version, for display ("Current version vX"). */
export const currentVersion = ref<string>("");
/** The version offered by the update feed, when one is available. */
export const newVersion = ref<string>("");
/** Release notes (markdown/plain) from the update manifest's `body`. */
export const releaseNotes = ref<string>("");
/** Last error message, shown in the dialog when `status === 'error'`. */
export const errorMessage = ref<string>("");

/** Download progress in bytes. `total` is 0 until the `Started` event lands. */
export const progress = ref<{ downloaded: number; total: number }>({
    downloaded: 0,
    total: 0,
});

/** User dismissed the notification bar for this available update. */
export const dismissed = ref<boolean>(false);
/** Whether the detail modal is open. */
export const dialogOpen = ref<boolean>(false);

/** The pending update handle, kept between check and install. */
let pending: Update | null = null;

/** Load this build's version for display. Safe to call repeatedly. */
export async function loadCurrentVersion(): Promise<void> {
    try {
        currentVersion.value = await getVersion();
    } catch (e) {
        console.warn("[Updater] could not read app version:", e);
    }
}

/**
 * Check the update feed.
 *
 * @param silent when true (startup check), staying up to date is invisible —
 *   only a found update surfaces. When false (manual button), the "up to date"
 *   result is shown so the click has visible feedback.
 */
export async function checkForUpdates(silent: boolean): Promise<void> {
    if (status.value === "checking" || status.value === "downloading") return;

    status.value = "checking";
    errorMessage.value = "";
    try {
        const update = await check();
        if (update) {
            pending = update;
            newVersion.value = update.version;
            releaseNotes.value = update.body ?? "";
            dismissed.value = false;
            status.value = "available";
        } else {
            pending = null;
            status.value = silent ? "idle" : "upToDate";
        }
    } catch (e) {
        errorMessage.value = String(e);
        status.value = "error";
        console.error("[Updater] check failed:", e);
    }
}

/**
 * Download and install the pending update, tracking byte progress. The app is
 * not relaunched automatically — that is the user's explicit "Restart now".
 */
export async function downloadAndInstallUpdate(): Promise<void> {
    if (!pending || status.value === "downloading") return;

    status.value = "downloading";
    errorMessage.value = "";
    progress.value = { downloaded: 0, total: 0 };
    try {
        await pending.downloadAndInstall((event) => {
            switch (event.event) {
                case "Started":
                    progress.value = {
                        downloaded: 0,
                        total: event.data.contentLength ?? 0,
                    };
                    break;
                case "Progress":
                    progress.value = {
                        ...progress.value,
                        downloaded:
                            progress.value.downloaded + event.data.chunkLength,
                    };
                    break;
                case "Finished":
                    status.value = "downloaded";
                    break;
            }
        });
        status.value = "downloaded";
    } catch (e) {
        errorMessage.value = String(e);
        status.value = "error";
        console.error("[Updater] download/install failed:", e);
    }
}

/** Relaunch into the freshly installed version. */
export async function restartApp(): Promise<void> {
    try {
        await relaunch();
    } catch (e) {
        errorMessage.value = String(e);
        status.value = "error";
        console.error("[Updater] relaunch failed:", e);
    }
}

/** Open the detail modal. */
export function openUpdateDialog(): void {
    dialogOpen.value = true;
}

/** Close the detail modal (no effect on the underlying update state). */
export function closeUpdateDialog(): void {
    dialogOpen.value = false;
}

/** Dismiss the notification bar for this update. */
export function dismissBanner(): void {
    dismissed.value = true;
}
