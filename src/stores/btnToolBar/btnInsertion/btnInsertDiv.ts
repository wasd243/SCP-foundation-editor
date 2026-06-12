import { EditorView, basicSetup } from 'codemirror';
import { html } from '@codemirror/lang-html';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorState, Prec } from '@codemirror/state';
import { keymap } from '@codemirror/view';

const DEFAULT_DIV_CONTENT = '<div >\n</div>';
const CURSOR_OFFSET = 5; // position right after `<div `

/**
 * This function is used to initialize the editor for a div block.
 * Tip: this function does not allow any `enter` key to insert a new line because wikidot does not support it. (or maybe, but not stable)
 */
export async function initDivEditor(parent: HTMLElement) {
    const view = new EditorView({
        doc: DEFAULT_DIV_CONTENT,
        extensions: [
            basicSetup,
            html(),
            oneDark,
            EditorState.allowMultipleSelections.of(false),
            Prec.highest(keymap.of([
                { key: 'Enter', run: () => true },
            ])),
            EditorView.lineWrapping,
            EditorView.theme({
                '&': { fontSize: '13px' },
            }),
        ],
        parent,
    });

    // place cursor right after `<div `
    view.dispatch({
        selection: { anchor: CURSOR_OFFSET, head: CURSOR_OFFSET },
    });
    view.focus();

    return view;
}

export function parseDivAttrs(input: string): Record<string, string> {
    const temp = document.createElement('div');
    temp.innerHTML = input.trim();

    const parsed = temp.querySelector('div');

    if (!parsed) return { 'data-editor-export': 'div' };

    const attrs: Record<string, string> = {};
    for (const attr of parsed.attributes) {
        attrs[attr.name] = attr.value;
    }

    attrs['data-editor-export'] = 'div';
    return attrs;
}

export function InsertDiv(view: EditorView, editor: any) {
    const content = view.state.doc.toString();
    const attrs = parseDivAttrs(content);

    editor.commands.insertContent({
        type: 'div',
        attrs: {
            tagName: 'div',
            htmlAttributes: {
                ...attrs,
                'data-editor-export': 'div',
            },
        },
        content: [{ type: 'paragraph' }],
    });
}
