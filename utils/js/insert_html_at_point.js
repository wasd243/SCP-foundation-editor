(function () {
    var editor = document.getElementById('editor-root');
    if (!editor) return;

    // 定位光标元素
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);

    // 我们定义哪些元素被认为是"组件"，碰到组件的话，就在它后面插入，或者替换它
    var compStr = '.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box';
    var comp = el ? el.closest(compStr) : null;

    // 创建一个临时的 template 元素来将字符串 HTML 解析为真正的 DOM 节点
    var template = document.createElement('template');
    template.innerHTML = __SAFE_HTML__.trim();

    // 解析出来的可能包含多个顶级节点（比如一个 div 外加一个结尾的 <p><br></p>）
    var frag = template.content;

    // 提取所有 <style> 标签并将它们移动到 <head> 中 (实现 CSS 置顶)
    var styles = frag.querySelectorAll('style');
    styles.forEach(function (styleTag) {
        if (!styleTag.hasAttribute('data-no-hoist')) {
            document.head.appendChild(styleTag);
        }
    });

    // 提取之后剩余的 HTML 将被当做实体节点插入
    var lastInsertedNode = frag.lastElementChild || frag.lastChild;

    if (comp) {
        // 如果是点击在某个已有的组件上面，且明确要替换（比如旧版警告逻辑里如果点在 div 上就替换）
        // 这里为了普遍适用，一律在所选组件之后插入
        comp.parentNode.insertBefore(frag, comp.nextSibling);

        // 如果你想实现在特定情况下覆盖替换，可以添加额外逻辑判断
        // if (comp.classList.contains('div-box')) { comp.parentNode.replaceChild(frag, comp); }
    } else {
        // 如果没有明确点在组件上，就直接附加到末尾
        editor.appendChild(frag);
    }
})();
