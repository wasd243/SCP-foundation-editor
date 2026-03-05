const COLOR_MAP = {
    'safe': '#27ae60',
    'euclid': '#f1c40f',
    'keter': '#c0392b',
    'neutralized': '#7f8c8d', // Gray
    'pending': '#bdc3c7',     // Light Gray
    'explained': '#95a5a6',   // Gray
    'esoteric': '#595959'     // Dark Gray
};



function toggleMonospace() {
    document.execCommand('styleWithCSS', false, true);
    const fontName = document.queryCommandValue('fontName');
    if (fontName.includes('Courier') || fontName.includes('monospace')) {
        document.execCommand('fontName', false, 'Verdana');
    } else {
        document.execCommand('fontName', false, 'Courier New');
    }
}

function toggleImgControls(btn) {
    const box = btn.closest('.image-block-box');
    box.classList.toggle('img-controls-hidden');
}



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

document.addEventListener('click', function (e) {
    // Explicitly handle ACS switch toggles to bypass contenteditable="false" click interception
    const switchLabel = e.target.closest('.acs-toggles .switch');
    if (switchLabel) {
        if (e.target.tagName !== 'INPUT') {
            const input = switchLabel.querySelector('input[type="checkbox"]');
            if (input) {
                input.checked = !input.checked;
                if (input.checked) {
                    switchLabel.classList.add('is-checked');
                } else {
                    switchLabel.classList.remove('is-checked');
                }
                input.dispatchEvent(new Event('change', { bubbles: true }));
                e.preventDefault();
                e.stopPropagation();
                return;
            }
        } else {
            // For direct input clicks (if they ever happen), also sync the class
            if (e.target.checked) {
                switchLabel.classList.add('is-checked');
            } else {
                switchLabel.classList.remove('is-checked');
            }
        }
    }

    const licHeader = e.target.closest('.license-header');
    // 排除license-header内的按钮点击（如原创按钮），避免误折叠
    if (licHeader && !e.target.closest('.btn-license-original')) {
        licHeader.parentElement.classList.toggle('open');
        return;
    }
    const colHeader = e.target.closest('.collapsible-header');
    if (colHeader && !e.target.closest('.title-input')) { colHeader.parentElement.classList.toggle('open'); }

    // Click-to-Insert-Newline on Right Side
    const comp = e.target.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
    if (comp && !comp.matches('.image-block-box')) {
        // Prevent triggering on interactive elements or headers
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT' || e.target.tagName === 'A' ||
            e.target.closest('.rate-controls') || e.target.closest('.license-header') || e.target.closest('.collapsible-header') || e.target.closest('.tab-header')) {
            return;
        }

        const rect = comp.getBoundingClientRect();
        const isRightSide = (e.clientX >= rect.right - Math.max(30, rect.width * 0.1)); // Right 10% or 30px

        if (isRightSide) {
            e.preventDefault();
            e.stopPropagation();

            // Check if next sibling is empty line
            let next = comp.nextElementSibling;
            if (!next || (next.tagName !== 'P' && next.tagName !== 'DIV') || next.innerText.trim() !== '') {
                const p = document.createElement('p');
                p.innerHTML = '<br>';
                comp.parentNode.insertBefore(p, next);
                next = p;
            }

            // Move cursor to the next line
            const range = document.createRange();
            range.selectNodeContents(next);
            range.collapse(true);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        }
    }
});

// ── 组件内可编辑字段换行隔离（带白名单）──
// 默认阻止 scp-component 内所有 contenteditable 子字段的 Enter 换行
// 白名单：内容区域（div/css模块、折叠块、tabview内容、表格单元格、脚注等）允许换行
document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    const target = e.target;
    if (!target) return;
    if (!target.isContentEditable) return;
    if (target.id === 'editor-root') return;
    const inComp = target.closest('.scp-component');
    if (!inComp) return;
    // ── 白名单：允许回车的元素或其祖先类 ──
    const ALLOW_SELECTORS = [
        '.div-content',          // div模块正文区
        '.css-content',          // css模块代码区
        '.collapsible-content-area', // 折叠块内容区
        '.tab-item',             // tabview 标签页内容
        'td[contenteditable]',   // 表格单元格（wikidot-table）
        'th[contenteditable]',   // 表格表头单元格
        '.scp-footnote',         // 脚注组件
        '.footnote-content',     // 脚注内容区
        '.basalt-doc-wrapper .doc-content', // 玄武岩文档内容
        '.basalt-content',       // 玄武岩内容区
        '.memo-content',         // Basalt memo 内容区
        '.acs-anim-checkbox',    // ACS 动画开关
        '.acs-shiver-checkbox',  // ACS 夜琉璃开关
    ];
    const isWhitelisted = ALLOW_SELECTORS.some(function (sel) {
        return target.closest(sel) !== null;
    });
    if (!isWhitelisted) {
        e.preventDefault();
        e.stopPropagation();
    }
}, true);

document.addEventListener('input', function (e) {
    // ACS Live Update
    const acsContainer = e.target.closest('[data-field="container"]');
    if (acsContainer && acsContainer.closest('.acs-box')) {
        const val = acsContainer.innerText.trim();
        applyAcsChange(acsContainer, val);
    }

    // Image Block Live Update
    const nameField = e.target.closest('.image-block-box [data-field="name"]');
    if (nameField) {
        if (typeof refreshImg === 'function') {
            refreshImg(nameField);
        }
    }

    const widthField = e.target.closest('.image-block-box [data-field="width"]');
    const heightField = e.target.closest('.image-block-box [data-field="height"]');
    if (widthField || heightField) {
        const box = e.target.closest('.image-block-box');
        if (box && typeof refreshImg === 'function') {
            const span = box.querySelector('[data-field="name"]');
            if (span) refreshImg(span);
        }
    }
});

document.addEventListener('change', function (e) {
    // Sync checkbox state for persistence (attribute vs property)
    if (e.target.matches('.acs-anim-checkbox, .acs-shiver-checkbox')) {
        if (e.target.checked) {
            e.target.setAttribute('checked', 'checked');
        } else {
            e.target.removeAttribute('checked');
        }
    }
});

// --- Smart Backspace Handler ---
document.addEventListener('keydown', function (e) {
    if (e.key === 'Backspace') {
        var sel = window.getSelection();
        if (sel.rangeCount > 0 && sel.isCollapsed) {
            var range = sel.getRangeAt(0);
            var node = range.startContainer;

            // Traverse up to find the block element if we are in a text node
            var block = node;
            while (block && block.nodeType === 3) block = block.parentNode;

            // Check for empty P or DIV with BR
            // If it's <p><br></p> or <div><br></div> and empty text
            if (block && (block.tagName === 'P' || block.tagName === 'DIV')) {
                if (block.innerText.trim() === '' || block.innerHTML === '<br>') {
                    // Check Previous and Next Siblings
                    var prev = block.previousElementSibling;
                    var next = block.nextElementSibling;

                    // Identify components
                    var isComp = function (el) {
                        return el && (el.classList.contains('scp-component') || el.classList.contains('div-box') || el.classList.contains('css-box') || el.hasAttribute('data-type'));
                    };

                    if (isComp(prev) && isComp(next)) {
                        e.preventDefault();
                        block.remove();
                        // Optional: Move cursor to end of prev?
                        // If we remove the line, cursor might be lost. 
                        // Let's try to set cursor to end of prev.
                        // But prev is contenteditable=false usually.
                        // So let's just remove it. Browser usually handles focus.
                    }
                }
            }
        }
    }
});



window.onload = function () {
    setupObserver();
    setupTooltips();
    refreshFootnotes();
};

window.addEventListener("load", function () {

    document.querySelectorAll('.acs-box [data-field="container"]').forEach(function (container) {
        const val = container.innerText.trim();
        applyAcsChange(container, val);
    });

    document.querySelectorAll('.image-block-box [data-field="name"]').forEach(span => {
        if (typeof refreshImg === 'function') {
            refreshImg(span, true);
        }
    });

});