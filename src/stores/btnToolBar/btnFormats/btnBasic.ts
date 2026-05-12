import { TextSelection } from "@tiptap/pm/state";
import { getEditor } from "../../editor.ts";

export function toggleEditorBold() {
    getEditor()?.chain().focus().toggleMark("bold").run();
}

export function toggleEditorItalic() {
    getEditor()?.chain().focus().toggleMark("italic").run();
}

export function toggleEditorUnderline() {
    getEditor()?.chain().focus().toggleMark("underline").run();
}

export function toggleEditorStrikethrough() {
    getEditor()?.chain().focus().toggleMark("strike").run();
}

export function toggleEditorSubscript() {
    getEditor()?.chain().focus().unsetMark("superscript").toggleMark("subscript").run();
}

export function toggleEditorSuperscript() {
    getEditor()?.chain().focus().unsetMark("subscript").toggleMark("superscript").run();
}

export function toggleEditorQuote() {
    getEditor()?.chain().focus().toggleWrap("blockquote").run();
}

export function insertEditorTable() {
    getEditor()
        ?.chain()
        .focus()
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
        .run();
}

export function insertEditorHorizontalRule() {
    getEditor()
        ?.chain()
        .focus()
        .setHorizontalRule()
        .run();
}

export function insertEditorCollapsible() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    const { state } = editor;
    const { $from, $to } = state.selection;
    const range = $from.blockRange($to);

    if (!range) {
        return;
    }

    const { schema } = state;
    const detailsType = schema.nodes.details;
    const detailsSummaryType = schema.nodes.detailsSummary;
    const detailsContentType = schema.nodes.detailsContent;
    const paragraphType = schema.nodes.paragraph;
    const showTextMark = schema.marks.collapsibleShowText;
    const hideTextMark = schema.marks.collapsibleHideText;

    if (!detailsType || !detailsSummaryType || !detailsContentType || !paragraphType || !showTextMark || !hideTextMark) {
        return;
    }

    if (!range.parent.canReplaceWith(range.startIndex, range.endIndex, detailsType)) {
        return;
    }

    const slice = state.doc.slice(range.start, range.end);
    const content = detailsContentType.contentMatch.matchFragment(slice.content)
        ? slice.content
        : paragraphType.createAndFill();

    if (!content) {
        return;
    }

    const summaryNode = detailsSummaryType.create(null, [
        schema.text("+", [showTextMark.create()]),
        schema.text("-", [hideTextMark.create()]),
    ]);
    const contentNode = detailsContentType.create(null, content);
    const detailsNode = detailsType.create(null, [summaryNode, contentNode]);
    const transaction = state.tr.replaceRangeWith(range.start, range.end, detailsNode);

    transaction.setSelection(TextSelection.create(transaction.doc, range.start + 2));
    transaction.scrollIntoView();

    editor.view.dispatch(transaction);
    editor.commands.focus();
}

export function btnBasicIdleInterface() {}
