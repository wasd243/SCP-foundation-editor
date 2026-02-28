(function () {
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var range = sel.getRangeAt(0);
        range.collapse(false);
        var editor = document.getElementById('editor-root');
        var lb = editor.querySelector('.license-box');

        // 这里的 __SAFE_HTML__ 将会被 Python 动态替换成真正的 HTML 代码
        var fragment = range.createContextualFragment('__SAFE_HTML__');
        var nodes = Array.from(fragment.childNodes);

        if (lb && (range.startContainer === editor && range.startOffset >= Array.from(editor.childNodes).indexOf(lb))) {
            editor.insertBefore(fragment, lb);
        } else {
            range.insertNode(fragment);
        }

        nodes.forEach(node => {
            if (node.nodeType === 1 && node.classList.contains('image-block-box')) {
                var nameSpan = node.querySelector('[data-field="name"]');
                if (nameSpan) refreshImg(nameSpan);
            }
        });

        if (fragment.lastChild) range.setStartAfter(fragment.lastChild);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
        if (typeof refreshFootnotes === 'function') refreshFootnotes();
    }
})();