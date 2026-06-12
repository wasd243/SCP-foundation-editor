import {EditorView, basicSetup} from 'codemirror';
import {html} from '@codemirror/lang-html';
import {oneDark} from '@codemirror/theme-one-dark';
import {EditorState} from '@codemirror/state';
import {keymap} from '@codemirror/view';

/**
 * This function is used to initialize the editor for a div block.
 * Tip: this function does not allow any `enter` key to insert a new line because wikidot does not support it. (or maybe, but not stable)
 */
export async function initDivEditor(parent: HTMLElement) {
    return new EditorView({
        doc: '',
        extensions: [
            basicSetup,
            html(),
            oneDark,
            EditorState.allowMultipleSelections.of(false),
            keymap.of([
                {key: 'Enter', run: () => true},
            ]),
            EditorView.lineWrapping,
            EditorView.theme({
                '&': {fontSize: '13px'},
            }),
        ],
        parent,
    });
}

export function parseDivAttrs(input: string): Record<string, string> {
    const temp = document.createElement('div');
    temp.innerHTML = `<div ${input}></div>`;

    const parsed = temp.firstElementChild as HTMLElement | null;

    // Add metadata for export
    if (!parsed) return {'data-editor-export': 'div'};

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
        // here use div tag when export
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
