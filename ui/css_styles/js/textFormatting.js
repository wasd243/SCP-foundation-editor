// textFormatting.js
// 包含文本段落级格式相关的处理函数：切换等宽字体()、字号调整

function toggleMonospace() {
    document.execCommand('styleWithCSS', false, true);
    const fontName = document.queryCommandValue('fontName');
    if (fontName.includes('Courier') || fontName.includes('monospace')) {
        document.execCommand('fontName', false, 'Verdana');
    } else {
        document.execCommand('fontName', false, 'Courier New');
    }
}

function applyFontSize(sizeValue) {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) return;
    const range = sel.getRangeAt(0);
    let targetNode = range.commonAncestorContainer;
    if (targetNode.nodeType === 3) targetNode = targetNode.parentNode;
    if (targetNode.classList.contains('size-span') && targetNode.innerText === sel.toString()) {
        targetNode.style.fontSize = sizeValue;
        const newRange = document.createRange();
        newRange.selectNodeContents(targetNode);
        sel.removeAllRanges(); sel.addRange(newRange);
    } else {
        const span = document.createElement('span');
        span.className = 'size-span';
        span.style.fontSize = sizeValue;
        try {
            const content = range.extractContents();
            span.appendChild(content);
            range.insertNode(span);
            const newRange = document.createRange();
            newRange.selectNodeContents(span);
            sel.removeAllRanges(); sel.addRange(newRange);
        } catch (e) { console.error(e); }
    }
}
