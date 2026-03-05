(function () {
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var range = sel.getRangeAt(0);

        // __HTML_CONTENT__ 会被替换成 json.dumps 处理后的安全 HTML 字符串
        var fragment = range.createContextualFragment(__HTML_CONTENT__);

        range.deleteContents();
        range.insertNode(fragment);

        if (typeof refreshFootnotes === 'function') refreshFootnotes();
    }
})();