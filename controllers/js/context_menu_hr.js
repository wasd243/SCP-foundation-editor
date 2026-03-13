// context_menu_hr.js
// 检测点击位置附近（±20px）是否命中 HR 分割线
(function () {
    for (var dy = -20; dy <= 20; dy += 4) {
        var el = document.elementFromPoint(__POS_X__, __POS_Y__ + dy);
        if (!el) continue;
        if (el.tagName === 'HR') return true;
        if (el.closest && el.closest('hr')) return true;
        if (el.parentElement && el.parentElement.tagName === 'HR') return true;
        if (el.parentElement && el.parentElement.querySelector && el.parentElement.querySelector('hr')) return true;
    }
    return false;
})()
