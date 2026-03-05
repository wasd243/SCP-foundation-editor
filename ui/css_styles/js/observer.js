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
}
