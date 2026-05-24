// If the editor content contains ~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~ and ~_WJ_NOTE_EXTERNAL_PARSER_END_~, alert the user
// because the user entered a [[note]] block without `[[note]]` or `[[/note]]`
import type { Editor } from "@tiptap/core";

const noteExternalParserMarkers = [
    "~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~",
    "~_WJ_NOTE_EXTERNAL_PARSER_END_~",
];

let alertActive = false;

export function contentHasNoteExternalParserMarkers(editor: Editor) {
    const text = editor.getText();
    const html = editor.getHTML();

    return noteExternalParserMarkers.some(marker =>
        text.includes(marker) || html.includes(marker),
    );
}

export function alertNoteExternalParserMarkers(editor: Editor) {
    const hasMarkers = contentHasNoteExternalParserMarkers(editor);

    if (!hasMarkers) {
        alertActive = false;
        return;
    }

    if (alertActive) {
        return;
    }

    alertActive = true;
    window.alert(
        "Internal note parser markers were found. Please remove ~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~ and ~_WJ_NOTE_EXTERNAL_PARSER_END_~ from the editor content.",
    );
}
