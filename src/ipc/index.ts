import { invoke } from '@tauri-apps/api/core';

export const api = {
    /**
     * front -> Rust -> ltmf -> Wikidot
     */
    convertToWikidot: async (nodes: any[]): Promise<string> => {
        return await invoke('export_wikidot', { elements: nodes });
    },

    /**
     * Wikidot -> HTML
     */
    parseToHtml: async (source: string): Promise<string> => {
        return await invoke('wikidot_to_html', { source });
    }
};