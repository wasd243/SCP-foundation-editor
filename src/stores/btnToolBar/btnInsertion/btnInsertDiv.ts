import { EditorView, basicSetup } from 'codemirror';
import { html } from '@codemirror/lang-html';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorState } from '@codemirror/state';
import { keymap } from '@codemirror/view';

export async function initDivEditor(parent: HTMLElement) {
    return new EditorView({
        doc: '',
        extensions: [
            basicSetup,
            html(),
            oneDark,
            EditorState.allowMultipleSelections.of(false),
            keymap.of([
                { key: 'Enter', run: () => true },
            ]),
            EditorView.lineWrapping,
            EditorView.theme({
                '&': { fontSize: '13px' },
            }),
        ],
        parent,
    });
}
