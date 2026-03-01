(function () {
    // 1. 注入解析好的 HTML 正文
    // __SAFE_HTML__ 会被 Python 替换为附带双引号的安全字符串
    document.getElementById('editor-root').innerHTML = __SAFE_HTML__;

    // 2. 注入提取的 CSS
    var style = document.getElementById('dynamic-terminal-style');
    if (!style) {
        style = document.createElement('style');
        style.id = 'dynamic-terminal-style';
        document.head.appendChild(style);
    }
    style.textContent = __SAFE_CSS__;

    // 刷新绑定事件
    if (typeof refreshFootnotes === 'function') refreshFootnotes();
    if (typeof setupObserver === 'function') setupObserver();

    // 3. 处理 Rate Module (评分模块) 状态
    const rateBox = document.querySelector('.rate-module-box');
    if (rateBox) {
        // __RATE_HIDDEN__ 会被替换为 true 或 false (无引号)
        if (__RATE_HIDDEN__) {
            rateBox.classList.add('hidden-rate');
            rateBox.setAttribute('data-hidden', 'true');
            const hideBtn = rateBox.querySelector('.rate-btn:nth-child(2)');
            if (hideBtn) hideBtn.innerText = '恢复';
        } else {
            rateBox.classList.remove('hidden-rate');
            rateBox.setAttribute('data-hidden', 'false');
            const hideBtn = rateBox.querySelector('.rate-btn:nth-child(2)');
            if (hideBtn) hideBtn.innerText = '隐藏';

            rateBox.removeAttribute('data-align');
            rateBox.querySelectorAll('.rate-align-btn').forEach(b => b.classList.remove('active'));

            // __RATE_ALIGN__ 会被替换为 "left", "right" 或 "" (有引号)
            const align = __RATE_ALIGN__;
            if (align === 'left') {
                const btn = rateBox.querySelector('.rate-align-btn:first-child');
                if (btn) rateAction('left', btn);
            } else if (align === 'right') {
                const btn = rateBox.querySelector('.rate-align-btn:last-child');
                if (btn) rateAction('right', btn);
            }
        }
    }
})();