import { EditorView, basicSetup } from "codemirror";
import { html } from "@codemirror/lang-html";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorState, Prec } from "@codemirror/state";
import { keymap } from "@codemirror/view";
import { TextSelection } from "@tiptap/pm/state";

const DEFAULT_SPAN_CONTENT = "<span ></span>";
const CURSOR_OFFSET = 6; // position right after `<span `

// Placeholder text inserted inside the span. An empty inline node cannot hold a
// caret in ProseMirror, so the span needs visible content; this placeholder is
// pre-selected on insert so the user can immediately type over it.
const DEFAULT_SPAN_TEXT = "text";

/**
 * This function is used to initialize the editor for a span block.
 * Tip: this function does not allow any `enter` key to insert a new line because wikidot does not support it. (or maybe, but not stable)
 */
export async function initSpanEditor(parent: HTMLElement) {
    const view = new EditorView({
        doc: DEFAULT_SPAN_CONTENT,
        extensions: [
            basicSetup,
            html(),
            oneDark,
            EditorState.allowMultipleSelections.of(false),
            Prec.highest(keymap.of([{ key: "Enter", run: () => true }])),
            EditorView.lineWrapping,
            EditorView.theme({
                "&": { fontSize: "13px" },
            }),
        ],
        parent,
    });

    // place cursor right after `<span `
    view.dispatch({
        selection: { anchor: CURSOR_OFFSET, head: CURSOR_OFFSET },
    });
    view.focus();

    return view;
}

export function parseSpanAttrs(input: string): Record<string, string> {
    const temp = document.createElement("div");
    temp.innerHTML = input.trim();

    const parsed = temp.querySelector("span");

    if (!parsed) return { "data-editor-export": "span" };

    const attrs: Record<string, string> = {};
    for (const attr of parsed.attributes) {
        attrs[attr.name] = attr.value;
    }

    attrs["data-editor-export"] = "span";
    return attrs;
}

export function InsertSpan(view: EditorView, editor: any) {
    const content = view.state.doc.toString();
    const attrs = parseSpanAttrs(content);

    // `[[span]]` is an inline node, so it must be inserted into a focused
    // selection inside a text block. Editing happened in the CodeMirror panel,
    // so the ProseMirror editor first needs `focus()` to restore a valid
    // selection; otherwise the insert lands nowhere and nothing appears.
    editor
        .chain()
        .focus()
        .command(({ tr, dispatch, state }: any) => {
            const inlineTag = state.schema.nodes.wjInlineTag;
            if (!inlineTag) return false;

            const span = inlineTag.create(
                {
                    tagName: "span",
                    htmlAttributes: {
                        ...attrs,
                        "data-editor-export": "span",
                    },
                },
                state.schema.text(DEFAULT_SPAN_TEXT),
            );

            if (dispatch) {
                const { from } = tr.selection;
                tr.insert(from, span);
                // Select the placeholder text inside the span so the user can
                // type over it; typed content stays inside the span.
                tr.setSelection(
                    TextSelection.create(
                        tr.doc,
                        from + 1,
                        from + 1 + DEFAULT_SPAN_TEXT.length,
                    ),
                );
            }

            return true;
        })
        .run();
}
