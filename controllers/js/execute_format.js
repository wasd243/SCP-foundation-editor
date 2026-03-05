(function () {
    const sel = window.getSelection();
    if (sel.rangeCount > 0) {
        let node = sel.anchorNode;
        if (node && node.nodeType === 3) node = node.parentNode;
        if (node && node.closest('a')) {
            // 阻止在链接内部进行样式覆盖，因为 Wikidot 不支持
            return;
        }
    }
    // 注意这里我们用了两个占位符：__COMMAND__ 和 __VAL_STR__
    document.execCommand('__COMMAND__', false, __VAL_STR__);
})();