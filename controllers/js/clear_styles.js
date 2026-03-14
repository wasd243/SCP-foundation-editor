// clear_styles.js
// 去除选中文字的字体大小和颜色样式，恢复到正文默认（无标签模式）
// 文字保护：跳过除折叠块内容区以外的 scp-component 内部文字
(function () {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;

    var range = sel.getRangeAt(0);
    if (range.collapsed) return;

    // 判断节点是否在受保护的 scp-component 内（非折叠块内容区）
    function isProtected(node) {
        var el = (node.nodeType === 3) ? node.parentNode : node;
        // 如果在折叠块内容区，则允许清除
        if (el.closest && el.closest('.collapsible-content-area')) return false;
        // 如果在任意其他 scp-component 内，则保护（跳过）
        if (el.closest && el.closest('.scp-component')) return true;
        return false;
    }

    // 在指定 container 内收集所有文本节点（包括 span）
    function collectNodes(container) {
        var walker = document.createTreeWalker(container, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null, false);
        var nodes = [];
        var node = walker.nextNode();
        while (node) {
            nodes.push(node);
            node = walker.nextNode();
        }
        return nodes;
    }

    // 清除某个 span 节点的字体大小和颜色（行内 style）
    function clearStyleOnEl(el) {
        if (!el.style) return;
        el.style.fontSize = '';
        el.style.color = '';
        // 如果 span 没有任何有用属性了，考虑 unwrap
        if (el.tagName === 'SPAN' && !el.getAttribute('style') && !el.className && el.attributes.length === 0) {
            var parent = el.parentNode;
            if (parent) {
                while (el.firstChild) parent.insertBefore(el.firstChild, el);
                parent.removeChild(el);
            }
        }
    }

    // 先用 surroundContents 克隆选区内容到一个临时容器来遍历
    var frag = range.cloneContents();
    var allEls = frag.querySelectorAll('span[style], font[color]');

    // 直接在 live DOM 上操作：获取选区内的所有 span[style] / font
    // 思路：遍历 range 内的所有 span，对非保护区域进行清除
    var rootContainer = range.commonAncestorContainer;
    if (rootContainer.nodeType === 3) rootContainer = rootContainer.parentNode;

    var spans = Array.from(rootContainer.querySelectorAll('span[style], font[color]'));

    spans.forEach(function (el) {
        if (!range.intersectsNode(el)) return;
        if (isProtected(el)) return;
        if (el.tagName === 'FONT') {
            el.removeAttribute('color');
            return;
        }
        clearStyleOnEl(el);
    });

    // 也处理 range 的 startContainer 和 endContainer 本身（如果是 span）
    function tryClean(node) {
        var el = (node.nodeType === 3) ? node.parentNode : node;
        if (el && el.tagName === 'SPAN' && el.style && !isProtected(el)) {
            clearStyleOnEl(el);
        }
    }
    tryClean(range.startContainer);
    tryClean(range.endContainer);
})();
