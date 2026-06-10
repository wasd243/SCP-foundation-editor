import {open} from '@tauri-apps/plugin-dialog';
import {readTextFile} from '@tauri-apps/plugin-fs';

/**
 * This function is used to open a file and parse it into the editor.
 * No `invoke` here because post-message and receiver `SyncToParser.ts` will automatically handle the parsing.
 * */
export async function OpenFtml() {
    const filePath = await open({
        filters: [{name: 'FTML', extensions: ['ftml']}],
        multiple: false,
    });

    // if user canceled the dialog
    if (!filePath) return;

    const content = await readTextFile(filePath as unknown as string);

    // directly use `parse_wikidot` function before opening
    window.postMessage(
        {type: 'code-view-content-changed', payload: content},
        '*'
    );
}
