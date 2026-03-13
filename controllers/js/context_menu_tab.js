// context_menu_tab.js
// 检测点击位置是否命中 TabView 的 tab-btn 按钮
(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    if (!el) return false;
    return !!(el.classList && el.classList.contains('tab-btn'));
})()
