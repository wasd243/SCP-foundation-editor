(function () {
    // 使用 __ELEMENT_ID__ 作为 ID 占位符
    var el = document.getElementById('__ELEMENT_ID__');
    if (el) {
        // 使用 __NEW_TEXT__ 作为内容的占位符（由 Python 注入 json.dumps 后的安全字符串）
        el.innerText = __NEW_TEXT__;
    }
})();