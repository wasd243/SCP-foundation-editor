(function () {
    const sel = window.getSelection();
    if (!sel.rangeCount) return;

    if (sel.isCollapsed) {
        let node = sel.anchorNode;
        if (node.nodeType === 3) node = node.parentNode;
        let hasColor = false;
        while (node && node.id !== 'editor-root') {
            if ((node.style && node.style.color) || (node.tagName && node.tagName.toUpperCase() === 'FONT' && node.hasAttribute('color'))) { hasColor = true; break; }
            node = node.parentNode;
        }

        if (hasColor) {
            const formats = {
                bold: document.queryCommandState('bold'),
                italic: document.queryCommandState('italic'),
                underline: document.queryCommandState('underline'),
                strike: document.queryCommandState('strikeThrough')
            };

            const range = sel.getRangeAt(0);
            const marker = document.createTextNode('\\u200B');
            range.insertNode(marker);

            const newRange = document.createRange();
            newRange.selectNode(marker);
            sel.removeAllRanges();
            sel.addRange(newRange);

            document.execCommand('RemoveFormat', false, null);

            if (formats.bold) document.execCommand('bold', false, null);
            if (formats.italic) document.execCommand('italic', false, null);
            if (formats.underline) document.execCommand('underline', false, null);
            if (formats.strike) document.execCommand('strikeThrough', false, null);

            sel.collapseToEnd();
        }
    } else {
        document.execCommand('RemoveFormat', false, 'foreColor');
    }
})();