// syncToolbar.js
// 包含编辑器工具栏状态同步的核心逻辑，通过 SelectionChange 时判断当前 DOM 的标签与样式，以反映加粗、颜色、字体等状态到工具栏图标

let syncTimeout = null;
function syncToolbarState() {
    clearTimeout(syncTimeout);
    syncTimeout = setTimeout(() => {
        const state = {
            bold: false,
            italic: false,
            underline: false,
            strike: false,
            sup: false,
            sub: false,
            ul: document.queryCommandState('insertUnorderedList'),
            ol: document.queryCommandState('insertOrderedList'),
            mono: false,
            color: false,
            heading: 0,
            align: 'left'
        };

        if (document.queryCommandState('justifyCenter')) state.align = 'center';
        if (document.queryCommandState('justifyRight')) state.align = 'right';
        if (document.queryCommandState('justifyFull')) state.align = 'justify';

        const sel = window.getSelection();
        if (sel.rangeCount > 0) {
            let node = sel.anchorNode;
            if (node && node.nodeType === 3) node = node.parentNode;
            let walk = node;
            while (walk && walk.id !== 'editor-root') {
                const tag = walk.tagName ? walk.tagName.toUpperCase() : '';

                // Tag checks
                if (tag === 'B' || tag === 'STRONG') state.bold = true;
                if (tag === 'I' || tag === 'EM') state.italic = true;
                if (tag === 'U') state.underline = true;
                if (tag === 'S' || tag === 'STRIKE' || tag === 'DEL') state.strike = true;
                if (tag === 'SUP') state.sup = true;
                if (tag === 'SUB') state.sub = true;
                if (tag === 'FONT' && walk.hasAttribute('color')) state.color = true;
                if (/^H[1-6]$/.test(tag)) {
                    state.heading = parseInt(tag.substring(1));
                }

                // Inline style checks
                if (walk.style) {
                    const fw = walk.style.fontWeight;
                    if (fw === 'bold' || parseInt(fw) >= 700) state.bold = true;
                    if (walk.style.fontStyle === 'italic') state.italic = true;
                    if ((walk.style.textDecoration || "").includes('underline')) state.underline = true;
                    if ((walk.style.textDecoration || "").includes('line-through')) state.strike = true;
                    if ((walk.style.fontFamily || "").includes('Courier New')) state.mono = true;
                    if (walk.style.color) state.color = true;
                }

                walk = walk.parentNode;
            }
        }

        console.log("SYNC_STATE:" + JSON.stringify(state));
    }, 50); // 50ms debounce
}
