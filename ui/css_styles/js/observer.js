// DOM 突变与行为监听的集中管理

// 玄武岩排版框架的布局监听器
var basaltObserver = new MutationObserver(function (mutations) {
    var needsLayout = false;
    mutations.forEach(function (mutation) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1 && node.classList && node.classList.contains('basalt-doc-wrapper')) {
                    needsLayout = true;
                }
            });
            mutation.removedNodes.forEach(function (node) {
                if (node.nodeType === 1 && node.classList && node.classList.contains('basalt-doc-wrapper')) {
                    needsLayout = true;
                }
            });
        }
    });
    if (needsLayout) {
        if (typeof updateBasaltDocLayout === 'function') {
            updateBasaltDocLayout();
        }
    }
});

// 编辑器主控制监听与初始化
function setupObserver() {
    const editor = document.getElementById('editor-root');
    if (!editor) return; // Guard

    // 核心文本内容、组件状态监听器
    const mainObserver = new MutationObserver((mutations) => {
        let needsRefresh = false;
        let contentChanged = false;

        mutations.forEach((mutation) => {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                needsRefresh = true;
                contentChanged = true;
            }
        });

        if (contentChanged) {
            try {
                if (typeof handleTitleMarkdown === 'function') handleTitleMarkdown();
            } catch (e) {
                console.error("Markdown Error: ", e);
            }
            try {
                if (typeof updateTerminalStyle === 'function') updateTerminalStyle(); // Check for CSS updates live
            } catch (e) {
                console.error("Style Update Error: ", e);
            }
        }

        if (needsRefresh && !document.activeElement.closest('#footnote-list-footer')) {
            try {
                if (typeof refreshFootnotes === 'function') refreshFootnotes();
            } catch (e) {
                console.error("Footnote Error: ", e);
            }
        }
    });
    mainObserver.observe(editor, { childList: true, characterData: true, subtree: true });

    // 给框架同时挂接玄武岩的监测
    basaltObserver.observe(editor, { childList: true, subtree: true });

    // Initial check
    if (typeof updateTerminalStyle === 'function') updateTerminalStyle();
    if (typeof updateBasaltDocLayout === 'function') updateBasaltDocLayout();

    // 工具栏状态追踪
    document.addEventListener('selectionchange', syncToolbarState);
    syncToolbarState();

    // 等宽字安全逻辑 (当开启等宽字时输入中文自动关闭)
    editor.addEventListener('input', (e) => {
        if (!window.monoSecurityEnabled) return;

        // 检测输入的文本是否包含中文
        // e.data 包含刚输入的字符，或者检查当前光标处的节点内容
        const inputData = e.data || "";
        const hasChinese = /[\u4e00-\u9fa5]/.test(inputData);

        if (hasChinese) {
            // 获取当前光标所在位置的字体
            const fontName = document.queryCommandValue('fontName') || "";
            if (fontName.includes('Courier') || fontName.includes('monospace')) {
                if (typeof toggleMonospace === 'function') {
                    toggleMonospace();
                    // 提示用户 (可选)
                    console.log("[Security] Monospace disabled due to Chinese input");
                    console.log("[等宽字安全] 等宽字已自动关闭，因为检测到中文字符输入");
                }
            }
        }
    });

    // 光标越界保护：防止光标落入两个半宽玄武岩文件框之间
    function enforceCursorRules() {
        var sel = window.getSelection();
        if (!sel || sel.rangeCount === 0) return;
        var range = sel.getRangeAt(0);
        if (!range.collapsed) return;

        var node = range.startContainer;
        var editor = document.getElementById('editor-root');
        if (!editor || !editor.contains(node)) return;

        var current = node;
        while (current && current.parentNode && current.parentNode !== editor) {
            current = current.parentNode;
        }

        if (current === editor || current.parentNode === editor) {
            var childNodes = editor.childNodes;
            var offset = -1;
            if (current === editor) {
                offset = range.startOffset;
            } else {
                offset = Array.prototype.indexOf.call(childNodes, current);
            }

            var prevNode = null;
            var searchLeft = (current === editor) ? offset - 1 : offset - 1;
            for (var i = searchLeft; i >= 0; i--) {
                var child = childNodes[i];
                if (child.nodeType === 1 && child.style && child.style.display !== 'none') {
                    if (child.tagName === 'BR' || (child.tagName === 'P' && child.innerText.trim() === '')) continue;
                    prevNode = child;
                    break;
                }
            }

            var nextNode = null;
            var searchRight = (current === editor) ? offset : offset + 1;
            for (var j = searchRight; j < childNodes.length; j++) {
                var child = childNodes[j];
                if (child.nodeType === 1 && child.style && child.style.display !== 'none') {
                    if (child.tagName === 'BR' || (child.tagName === 'P' && child.innerText.trim() === '')) continue;
                    nextNode = child;
                    break;
                }
            }

            if (prevNode && nextNode &&
                prevNode.classList && prevNode.classList.contains('basalt-doc-wrapper') && prevNode.classList.contains('half-width') &&
                nextNode.classList && nextNode.classList.contains('basalt-doc-wrapper') && nextNode.classList.contains('half-width')) {
                var newRange = document.createRange();
                newRange.setStartAfter(nextNode);
                newRange.collapse(true);
                sel.removeAllRanges();
                sel.addRange(newRange);
            }
        }
    }

    document.addEventListener('selectionchange', enforceCursorRules);
}
