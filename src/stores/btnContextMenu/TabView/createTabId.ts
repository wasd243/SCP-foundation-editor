// createTabId.ts is used to create IDs for tabs in the TipTap editor

export function createTabId() {
    return `wj-id-${Date.now().toString(36)}`;
}