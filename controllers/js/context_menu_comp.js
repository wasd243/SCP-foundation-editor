// context_menu_comp.js
// 检测点击位置命中的 .scp-component 并返回其 data-type
(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    if (!el) return null;
    var c = el.closest('.scp-component');
    return c ? c.getAttribute('data-type') : null;
})()
