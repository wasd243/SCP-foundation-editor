// context_menu_fn.js
// 返回点击位置命中的脚注在脚注列表中的索引（-1 表示未命中）
(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    if (!el) return -1;
    var fn = el.closest('.scp-footnote');
    return fn ? Array.from(document.querySelectorAll('.scp-footnote')).indexOf(fn) : -1;
})()
