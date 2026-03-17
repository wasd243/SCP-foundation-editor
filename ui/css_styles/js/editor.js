/**
 * ============================================================
 * SCP Foundation WYSIWYG Editor
 *
 * Copyright (C) 2026 Zichen Wang (wasd243)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License v3.
 *
 * This program is distributed WITHOUT ANY WARRANTY.
 *
 * https://www.gnu.org/licenses/agpl-3.0.html
 * ============================================================
 */
window.addEventListener("load", function () {
    // ----------------------------------------
    // 1. 初始化核心观察器与基础 UI
    // ----------------------------------------
    setupObserver();
    setupTooltips();
    refreshFootnotes();

    // ----------------------------------------
    // 2. 初始化按需渲染的动态组件 (如 ACS/Image)
    // ----------------------------------------

    // 初始化 ACS 异常分类标签的回显颜色
    document.querySelectorAll('.acs-box [data-field="container"]').forEach(function (container) {
        const val = container.innerText.trim();
        if (typeof applyAcsChange === 'function') {
            applyAcsChange(container, val);
        }
    });

    // 初始化 Image Block 的回显或预加载
    document.querySelectorAll('.image-block-box [data-field="name"]').forEach(span => {
        if (typeof refreshImg === 'function') {
            refreshImg(span, true);
        }
    });

    // 拦截粘贴事件，只粘贴纯文本
    document.getElementById('editor-root').addEventListener('paste', function(e) {
        e.preventDefault();
        var text = '';
        if (e.clipboardData || e.originalEvent && e.originalEvent.clipboardData) {
            text = (e.originalEvent || e).clipboardData.getData('text/plain');
        } else if (window.clipboardData) {
            text = window.clipboardData.getData('Text');
        }
        if (document.queryCommandSupported('insertText')) {
            document.execCommand('insertText', false, text);
        } else {
            document.execCommand('paste', false, text);
        }
    });
});
