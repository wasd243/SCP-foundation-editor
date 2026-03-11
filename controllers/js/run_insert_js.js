(function () {
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var range = sel.getRangeAt(0);

        // __HTML_CONTENT__ 会被替换成 json.dumps 处理后的安全 HTML 字符串
        var fragment = range.createContextualFragment(__HTML_CONTENT__);

        var lastChild = fragment.lastChild;
        range.deleteContents();
        range.insertNode(fragment);
        
        if (lastChild) {
            range.setStartAfter(lastChild);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }

        if (typeof refreshFootnotes === 'function') refreshFootnotes();
    }
})();