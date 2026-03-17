// context_menu_hr.js
// 检测点击位置附近（±15px）是否命中 HR 分割线（精确匹配）
(function () {
    for (var dy = -15; dy <= 15; dy += 3) {
        var el = document.elementFromPoint(__POS_X__, __POS_Y__ + dy);
        if (!el) continue;
        // 只在元素自身或其直接父元素是 HR 时匹配，不用 querySelector 防止宽泛匹配
        if (el.tagName === 'HR') return true;
        if (el.parentElement && el.parentElement.tagName === 'HR') return true;
    }
    return false;
})()
