import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";

/**
 * Ignored-lines settings store.
 *
 * Shared reactive state + helpers for the "Ignored lines" settings section.
 * This store is the single source of truth for parsing, validating, and merging
 * line ranges (so the UI gets instant feedback); the Rust side only persists the
 * canonical token list and defensively re-validates it. Mirrors the `savesPath`
 * store: reactive refs + thin async helpers over `invoke`.
 */

/** A canonical, inclusive line range. A single line is `start === end`. */
export type IgnoreRange = { start: number; end: number };

/** The merged, ascending list of ignored ranges. */
export const ignoreRanges = ref<IgnoreRange[]>([]);
/** Last validation/persistence error, or null when the last action succeeded. */
export const ignoreLinesError = ref<string | null>(null);

const SINGLE = /^\d+$/;
const RANGE = /^(\d+)\s*-\s*(\d+)$/;

/**
 * Parse `"7"` or `"1-10"` into a canonical range. Throws an `Error` whose message
 * is shown to the user. A range with `x === y` collapses to a single line.
 */
export function parseRange(input: string): IgnoreRange {
    const text = input.trim();

    if (SINGLE.test(text)) {
        const n = Number(text);
        if (n < 1) throw new Error("Line numbers start at 1.");
        return { start: n, end: n };
    }

    const match = RANGE.exec(text);
    if (match) {
        const start = Number(match[1]);
        const end = Number(match[2]);
        if (start < 1 || end < 1) throw new Error("Line numbers start at 1.");
        if (end < start)
            throw new Error("A range goes low to high — try 1-10, not 10-1.");
        return { start, end };
    }

    throw new Error("Enter a line number like 7, or a range like 1-10.");
}

/** Merge overlapping or adjacent ranges into a sorted, canonical list. */
export function mergeRanges(list: IgnoreRange[]): IgnoreRange[] {
    const sorted = [...list].sort((a, b) => a.start - b.start);
    const out: IgnoreRange[] = [];

    for (const range of sorted) {
        const last = out[out.length - 1];
        // `<= last.end + 1` fuses both overlapping (5 in 1-10) and adjacent
        // (4 right after 1-3) ranges.
        if (last && range.start <= last.end + 1) {
            last.end = Math.max(last.end, range.end);
        } else {
            out.push({ ...range });
        }
    }

    return out;
}

/** Display form: `7` or `1–10` (en dash). */
export const formatRange = (r: IgnoreRange): string =>
    r.start === r.end ? `${r.start}` : `${r.start}–${r.end}`;

/** Storage form: `7` or `1-10` (hyphen), as persisted and re-parsed. */
const toToken = (r: IgnoreRange): string =>
    r.start === r.end ? `${r.start}` : `${r.start}-${r.end}`;

/** Load the saved ranges from the backend. Malformed tokens are skipped. */
export async function loadIgnoreLines(): Promise<void> {
    try {
        const tokens = await invoke<string[]>("read_ignore_lines_metadata");
        const ranges: IgnoreRange[] = [];
        for (const token of tokens) {
            try {
                ranges.push(parseRange(token));
            } catch {
                // A hand-edited or stale token shouldn't break the list.
            }
        }
        ignoreRanges.value = mergeRanges(ranges);
        ignoreLinesError.value = null;
    } catch (e) {
        ignoreLinesError.value = String(e);
        console.error("[IgnoreLines] load failed:", e);
    }
}

/**
 * Validate and add `input` to the list, then persist. Returns whether it was
 * accepted; on a parse error the message lands in `ignoreLinesError` and nothing
 * is written.
 */
export async function addIgnoreLine(input: string): Promise<boolean> {
    let range: IgnoreRange;
    try {
        range = parseRange(input);
    } catch (e) {
        ignoreLinesError.value = e instanceof Error ? e.message : String(e);
        return false;
    }

    ignoreLinesError.value = null;
    ignoreRanges.value = mergeRanges([...ignoreRanges.value, range]);
    await persist();
    return true;
}

/** Remove the range at `index`, then persist. */
export async function removeIgnoreLine(index: number): Promise<void> {
    ignoreRanges.value = ignoreRanges.value.filter((_, i) => i !== index);
    await persist();
}

async function persist(): Promise<void> {
    try {
        await invoke("write_ignore_lines_metadata", {
            lines: ignoreRanges.value.map(toToken),
        });
    } catch (e) {
        ignoreLinesError.value = String(e);
        console.error("[IgnoreLines] save failed:", e);
    }
}
