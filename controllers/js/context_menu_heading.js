// context_menu_heading.js
// 检测点击位置是否命中标题标签 (H1-H6)
(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    if (!el) return null;
    
    // 向上查找最近的标题标签
    var h = el.closest('h1, h2, h3, h4, h5, h6');
    if (h) {
        if (!h.id) {
            h.id = "temp-heading-id-" + Math.random().toString(36).substr(2, 9);
        }
        var anchor = h.getAttribute('data-toc-anchor');
        if (!anchor) {
            var marker = h.querySelector('.toc-anchor-marker');
            if (marker) anchor = marker.getAttribute('data-anchor');
        }
        return {
            id: h.id,
            tagName: h.tagName.toLowerCase(),
            text: h.innerText.trim(),
            anchor: anchor || ""
        };
    }
    return null;
})()
