// Registry + styling helpers for the footnote sub-editor.
//
// A footnote is edited inside a nested ProseMirror `EditorView` (see
// FootnoteE.ts). While that inner view is open, the *outer* editor's selection
// is a NodeSelection covering the whole footnote node, so toolbar style
// commands dispatched to the main editor restyle the entire footnote line.
//
// This module tracks the currently-open inner view and exposes helpers that
// apply inline-mark styles to its own text selection instead. Inner steps are
// mapped back onto the outer document by FootnoteView.dispatchInner, so no
// node-spec or serialization changes are needed.
//
// Every helper returns `true` when it handled the action (a footnote sub-editor
// is open) so callers can fall through to the main editor otherwise. Note it
// returns `true` even when the requested mark type is missing — that is
// deliberate, to avoid falling through and restyling the whole node.
import { toggleMark } from "@tiptap/pm/commands";
import type { MarkType } from "@tiptap/pm/model";
import type { EditorView } from "@tiptap/pm/view";

let activeFootnoteView: EditorView | null = null;

export function setActiveFootnoteView(view: EditorView) {
    activeFootnoteView = view;
}

// Only clears when the passed view is the one stored. When a footnote is
// clicked while another is open, the new footnote's `open()` may run before the
// previous footnote's `close()` during the same selection update; this guard
// stops the stale `close()` from wiping the freshly-registered view.
export function clearActiveFootnoteView(view: EditorView) {
    if (activeFootnoteView === view) {
        activeFootnoteView = null;
    }
}

export function getActiveFootnoteView(): EditorView | null {
    return activeFootnoteView;
}

// Removes `markType` from the current selection (used to enforce sub/sup mutual
// exclusion before toggling the other on).
function removeMarkFromSelection(view: EditorView, markType: MarkType) {
    const { from, to, empty } = view.state.selection;

    if (empty) {
        if (markType.isInSet(view.state.storedMarks ?? [])) {
            view.dispatch(view.state.tr.removeStoredMark(markType));
        }

        return;
    }

    view.dispatch(view.state.tr.removeMark(from, to, markType));
}

export function toggleFootnoteMark(
    markName: string,
    excludesMarkName?: string,
): boolean {
    const view = getActiveFootnoteView();

    if (!view) {
        return false;
    }

    const markType = view.state.schema.marks[markName];

    if (!markType) {
        return true;
    }

    if (excludesMarkName) {
        const excludesType = view.state.schema.marks[excludesMarkName];

        if (excludesType) {
            removeMarkFromSelection(view, excludesType);
        }
    }

    toggleMark(markType)(view.state, (tr) => view.dispatch(tr));
    view.focus();

    return true;
}

export function setFootnoteMark(
    markName: string,
    attrs: Record<string, unknown>,
): boolean {
    const view = getActiveFootnoteView();

    if (!view) {
        return false;
    }

    const markType = view.state.schema.marks[markName];

    if (!markType) {
        return true;
    }

    const { from, to, empty } = view.state.selection;
    const mark = markType.create(attrs);

    if (empty) {
        view.dispatch(view.state.tr.addStoredMark(mark));
    } else {
        view.dispatch(view.state.tr.addMark(from, to, mark));
    }

    view.focus();

    return true;
}

export function addFontSizeOverSelection(
    attrs: Record<string, unknown>,
): boolean {
    const view = getActiveFootnoteView();

    if (!view) {
        return false;
    }

    const markType = view.state.schema.marks.fontSize;

    if (!markType) {
        return true;
    }

    const { from, to } = view.state.selection;
    const tr = view.state.tr;
    const mark = markType.create(attrs);
    let applied = false;

    tr.doc.nodesBetween(from, to, (node, pos) => {
        if (!node.isText) {
            return;
        }

        tr.addMark(pos, pos + node.nodeSize, mark);
        applied = true;
    });

    if (applied) {
        view.dispatch(tr);
        view.focus();
    }

    return true;
}

// Reads the fontSize attr from the active footnote selection so the
// increase/decrease buttons step from the footnote's current value. Returns
// `null` when no footnote is open or no fontSize mark is present.
export function getActiveFootnoteFontSize(): string | null {
    const view = getActiveFootnoteView();

    if (!view) {
        return null;
    }

    const markType = view.state.schema.marks.fontSize;

    if (!markType) {
        return null;
    }

    const { from, $from, empty } = view.state.selection;
    const marks = empty
        ? view.state.storedMarks ?? $from.marks()
        : view.state.doc.resolve(from).marks();
    const mark = marks.find((candidate) => candidate.type === markType);
    const size = mark?.attrs.size;

    return typeof size === "string" ? size : null;
}

export function clearFootnoteMarks(): boolean {
    const view = getActiveFootnoteView();

    if (!view) {
        return false;
    }

    const { from, to, empty } = view.state.selection;

    if (empty) {
        view.dispatch(view.state.tr.setStoredMarks([]));
    } else {
        view.dispatch(view.state.tr.removeMark(from, to));
    }

    view.focus();

    return true;
}
