(function () {
    const editor = document.getElementById('editor-root');
    if (!editor) return;

    // 1. 获取坐标并定义占位符
    const x = __POS_X__;
    const y = __POS_Y__;
    const cssContent = __SAFE_CSS__; // 补上这个 Python 正在找的占位符
    const htmlContent = __SAFE_HTML__;

    // 2. 如果有 CSS 内容，直接注入到 head
    if (cssContent && cssContent.trim()) {
        const style = document.createElement('style');
        style.setAttribute('data-type', 'injected-terminal-css');
        style.textContent = cssContent;
        document.head.appendChild(style);
    }

    // 3. 定位插入点
    const el = document.elementFromPoint(x, y);
    const compStr = '.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box';
    const comp = el ? el.closest(compStr) : null;

    const template = document.createElement('template');
    template.innerHTML = htmlContent.trim();
    const frag = template.content;

    // 4. 处理 HTML 内部可能自带的 <style> (保留你原有的逻辑)
    const styles = frag.querySelectorAll('style');
    styles.forEach(styleTag => {
        if (!styleTag.hasAttribute('data-no-hoist')) {
            document.head.appendChild(styleTag);
        }
    });

    // 5. 插入 DOM
    if (comp) {
        comp.parentNode.insertBefore(frag, comp.nextSibling);
    } else {
        editor.appendChild(frag);
    }
})();