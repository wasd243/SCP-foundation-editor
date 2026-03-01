(function () {
    // 使用 __INDEX__ 作为索引占位符
    var fn = document.querySelectorAll('.scp-footnote')[__INDEX__];
    if (fn) {
        // 使用 __NEW_TEXT__ 作为内容的占位符
        fn.setAttribute('data-content', __NEW_TEXT__);
        fn.setAttribute('title', __NEW_TEXT__);
        refreshFootnotes();
    }
})();