// createTabId.ts is used to create IDs for tabs in the TipTap editor

export function createTabId() {
    return `wj-id-${crypto.randomUUID()}`;
}
