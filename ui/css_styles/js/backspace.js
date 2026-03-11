// Backspace Event Handling Logic

document.addEventListener('keydown', function (e) {
    if (e.key === 'Backspace') {
        const sel = window.getSelection();
        if (!sel.rangeCount || !sel.isCollapsed) return;

        // Smart Backspace: Delete empty line between Component and Body Text
        const smartNode = sel.anchorNode;
        const smartBlock = smartNode.nodeType === 3 ? smartNode.parentElement : smartNode;

        if (smartBlock && (smartBlock.tagName === 'P' || smartBlock.tagName === 'DIV') && smartBlock.innerText.replace(/\n/g, '').trim() === '') {
            const prev = smartBlock.previousElementSibling;
            const next = smartBlock.nextElementSibling;
            if (prev && next) {
                // Refined: Exclude Image Blocks (.image-block-box)
                const isComp = prev.matches && prev.matches('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
                const isImage = prev.matches && prev.matches('.image-block-box');

                // Check if next is body text (has content)
                const hasContent = next.innerText && next.innerText.trim().length > 0;

                if (isComp && !isImage && hasContent) {
                    e.preventDefault();
                    smartBlock.remove();
                    const newR = document.createRange();
                    // Refined: set cursor AFTER the previous component (visually to its right/end)
                    if (prev) newR.setStartAfter(prev);
                    newR.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(newR);
                    return;
                }
            }
        }

        // Fix: Prevent cursor disappearing when backspacing against a component
        const range = sel.getRangeAt(0);
        if (range.startOffset === 0) {
            let node = range.startContainer;
            if (node.nodeType === 3) {
                if (node.previousSibling && node.previousSibling.nodeType === 1 && node.previousSibling.classList.contains('scp-component')) {
                    e.preventDefault(); return;
                }
                if (!node.previousSibling) node = node.parentNode;
            }
            if (node.nodeType === 1 && node.previousElementSibling && node.previousElementSibling.classList.contains('scp-component')) {
                e.preventDefault(); return;
            }
        }

        const anchor = sel.anchorNode;
        const element = anchor.nodeType === 3 ? anchor.parentElement : anchor;
        const blockquote = element.closest('blockquote');
        if (blockquote) {
            const range = document.createRange();
            range.selectNodeContents(blockquote);
            range.setEnd(sel.anchorNode, sel.anchorOffset);
            if (range.toString().trim() === '') {
                document.execCommand('formatBlock', false, 'p');
            }
        }
        const li = element.closest('li');
        if (li) {
            if (li.textContent.trim() === '') {
                document.execCommand('outdent');
                if (li.closest('ul, ol') && li.parentElement.children.length === 1) {
                    document.execCommand('formatBlock', false, 'p');
                }
            }
        }
    }
});
