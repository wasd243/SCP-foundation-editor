function handleTitleMarkdown() {
    // 处理标题的 Markdown 语法
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    const range = sel.getRangeAt(0);
    let node = range.startContainer;
    let block = node;
    while (block && block.parentNode && block.parentNode.id !== 'editor-root') block = block.parentNode;
    if (block && block.nodeType === 1 && block.id !== 'editor-root') {
        const text = block.innerText;
        // Avoid unnecessary regex matches on empty lines or non-title lines
        if (!text || !text.startsWith('+')) return;

        const match = text.match(new RegExp("^([+]{1,6})\\\\s+(.*)"));
        if (match) {
            const level = match[1].length;
            const content = match[2];
            const hTag = 'H' + level;
            if (block.tagName !== hTag) {
                const newH = document.createElement(hTag);
                newH.innerText = content;
                block.parentNode.replaceChild(newH, block);
                const newRange = document.createRange();
                newRange.selectNodeContents(newH);
                newRange.collapse(false);
                sel.removeAllRanges();
                sel.addRange(newRange);
            }
        }
    }
}