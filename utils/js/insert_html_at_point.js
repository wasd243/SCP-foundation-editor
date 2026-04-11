(function () {
    // 运行时由 Python 字符串替换注入，无需声明
    var posX = __POS_X__;
    var posY = __POS_Y__;
    var safeHtml = __SAFE_HTML__;

    var editor = document.getElementById('editor-root');
    if (!editor) {
        console.error('[insert_html] 找不到 #editor-root，注入中止');
        return;
    }

    // 定位点击坐标下的元素
    var el = document.elementFromPoint(posX, posY);

    // 判断是否点在已有组件上
    var compStr = '.scp-component, .acs-box, .rate-module-box, .tabview-box, ' +
        '.collapsible-box, .license-box, .wikidot-table, .div-box, ' +
        '.css-box, .raisa-box, .class-warning-box';
    var comp = el ? el.closest(compStr) : null;

    // 将 HTML 字符串解析为真实 DOM 节点片段
    var template = document.createElement('template');
    template.innerHTML = safeHtml.trim();
    var frag = template.content;

    // ── CSS 置顶：把 <style> 提升到 <head>（标记了 data-no-hoist 的除外）──
    var styles = frag.querySelectorAll('style');
    styles.forEach(function (styleTag) {
        if (!styleTag.hasAttribute('data-no-hoist')) {
            document.head.appendChild(styleTag);
        }
    });

    // ── 修复换行 Bug：插入后追加空段落，确保光标有地方落脚 ──
    var trailingP = document.createElement('p');
    trailingP.innerHTML = '<br>';
    frag.appendChild(trailingP);

    // ── 执行插入 ──
    if (comp && comp.parentNode) {
        // 点在已有组件上：在该组件之后插入
        comp.parentNode.insertBefore(frag, comp.nextSibling);
    } else {
        // 否则追加到编辑器末尾
        editor.appendChild(frag);
    }

    // ── 修复换行 Bug：将光标移动到刚插入的尾部段落内 ──
    var sel = window.getSelection();
    if (sel && trailingP.isConnected) {
        var range = document.createRange();
        range.setStart(trailingP, 0);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
        trailingP.scrollIntoView({block: 'nearest'});
    }
})();