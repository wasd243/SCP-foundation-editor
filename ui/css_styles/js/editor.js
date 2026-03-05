window.addEventListener("load", function () {
    // ----------------------------------------
    // 1. 初始化核心观察器与基础 UI
    // ----------------------------------------
    setupObserver();
    setupTooltips();
    refreshFootnotes();

    // ----------------------------------------
    // 2. 初始化按需渲染的动态组件 (如 ACS/Image)
    // ----------------------------------------

    // 初始化 ACS 异常分类标签的回显颜色
    document.querySelectorAll('.acs-box [data-field="container"]').forEach(function (container) {
        const val = container.innerText.trim();
        if (typeof applyAcsChange === 'function') {
            applyAcsChange(container, val);
        }
    });

    // 初始化 Image Block 的回显或预加载
    document.querySelectorAll('.image-block-box [data-field="name"]').forEach(span => {
        if (typeof refreshImg === 'function') {
            refreshImg(span, true);
        }
    });
});