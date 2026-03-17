// componentEvents.js
// 包含所有点击、输入、改变、键盘回车等用户对独立组件进行操作交互时的事件代理监听器
// 包括：组件的折叠展开、点击换行、组件内阻止默认回车的白名单判定、Image和ACS相关表单的数据 Live Update 等

function toggleImgControls(btn) {
    const box = btn.closest('.image-block-box');
    box.classList.toggle('img-controls-hidden');
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
    if (comp && !comp.matches('.image-block-box') && !comp.matches('.wikidot-table') && !comp.matches('.aim-box') && !comp.matches('.user-tag')) {
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
        '.terminal-shortcut-box',// 终端样式快捷插入组件允许回车
        '.terminal-001-box',     // 终端#001组件允许回车
        '.raisa-notice',         // RAISA通知组件
        '.page-note-box'         // 便签纸组件允许回车
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
