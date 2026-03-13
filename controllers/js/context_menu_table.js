// context_menu_table.js
// 检测点击位置是否在 wikidot 表格内
(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    if (!el) return false;
    return !!el.closest('table.wikidot-table');
})()
