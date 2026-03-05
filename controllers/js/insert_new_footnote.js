(function () {
    var fns = document.querySelectorAll('.scp-footnote');
    var nextNum = fns.length + 1;
    var span = document.createElement('span');
    span.className = 'scp-component scp-footnote';
    span.setAttribute('data-type', 'footnote');
    span.setAttribute('data-content', '新脚注内容');
    span.setAttribute('contenteditable', 'false');
    span.innerText = nextNum;
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var range = sel.getRangeAt(0);
        range.insertNode(span);
        range.setStartAfter(span);
        range.collapse(true);
        sel.removeAllRanges(); sel.addRange(range);
    }
    refreshFootnotes();
})()