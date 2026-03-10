function refreshImg(span, force) {
    const box = span.closest('.image-block-box');
    const img = box.querySelector('.img-preview');
    const placeholder = box.querySelector('.img-placeholder');
    const nameField = box.querySelector('[data-field="name"]');
    let url = nameField ? nameField.textContent.trim() : '';

    if (url && (url.startsWith('http') || url.startsWith('//'))) {
        if (force) {
            const sep = url.includes('?') ? '&' : '?';
            img.src = url + sep + "t=" + Date.now();
        } else {
            img.src = url;
        }
        img.style.display = 'block';
        placeholder.style.display = 'none';
        img.onerror = function () {
            // 弹窗提示
            alert("加载失败，真实 src 是：" + img.src);
            console.log("加载失败，真实 src 是：" + img.src);
            img.style.display = 'none';
            placeholder.style.display = 'block';
            placeholder.textContent = '[无效的图片链接]';
        }
    } else {
        // 图片预览区域
        img.style.display = 'none';
        placeholder.style.display = 'block';
        placeholder.textContent = '[图片预览区域]';
    }

    const wSpan = box.querySelector('[data-field="width"]');
    const hSpan = box.querySelector('[data-field="height"]');

    if (wSpan) {
        let w = wSpan.textContent.trim();
        if (!w) {
            w = "auto";
            wSpan.textContent = "auto";
        } else if (!isNaN(w)) {
            w += "px";
        }
        img.style.width = w;
    }

    if (hSpan) {
        let h = hSpan.textContent.trim();
        if (!h) {
            h = "auto";
            hSpan.textContent = "auto";
        } else if (!isNaN(h)) {
            h += "px";
        }
        img.style.height = h;
    }
}

function refreshAllImgs(force) {
    document.querySelectorAll('.image-block-box [data-field="name"]').forEach(span => {
        refreshImg(span, force);
    });
}

// 编辑图片链接
function editImgLink(label) {
    const box = label.closest('.image-block-box');
    const nameSpan = box.querySelector('[data-field="name"]');
    const oldUrl = nameSpan.textContent.trim();
    const newUrl = window.prompt("请输入图片链接:", oldUrl);
    if (newUrl !== null) {
        nameSpan.textContent = newUrl;
        refreshImg(nameSpan);
    }
}

function setImgAlign(btn, align) {
    const box = btn.closest('.image-block-box');
    if (box) {
        box.setAttribute('data-align', align);
        if (align === 'center') {
            const img = box.querySelector('.img-preview');
            if (img) img.style.width = '100%';
        } else {
            // Optionally restore original width if needed, but refreshImg handles it
            refreshImg(box.querySelector('[data-field="name"]'));
        }
    }
}

function rateAction(action, btn) {
    const box = btn.closest('.rate-module-box');
    if (action === 'hide') {
        if (box.classList.contains('hidden-rate')) {
            box.classList.remove('hidden-rate');
            box.setAttribute('data-hidden', 'false');
            btn.textContent = '隐藏';
        } else {
            box.classList.add('hidden-rate');
            box.setAttribute('data-hidden', 'true');
            btn.textContent = '恢复';
        }
    } else if (action === 'left' || action === 'right') {
        // Toggle logic: if already active, clear it? Or just switch.
        // User request: "left, right ... click to cancel". 
        // Actually prompt said: "Hide... click to cancel rendering... click again to restore". 
        // For alignment: "left... right...".
        // Let's implement radio-like behavior for alignment.

        const currentAlign = box.getAttribute('data-align');
        if (currentAlign === action) {
            box.removeAttribute('data-align');
            btn.classList.remove('active');
        } else {
            box.setAttribute('data-align', action);
            box.querySelectorAll('.rate-align-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
    }
}

// Paste handler for cleaning links
document.addEventListener('paste', function (e) {
    const target = e.target;
    // Check for image link field OR secondary icon field OR license box fields
    if (target.matches('.image-block-box [data-field="name"]') ||
        target.closest('.image-block-box [data-field="name"]') ||
        target.matches('.acs-box [data-field="secondary-icon"]') ||
        target.closest('.acs-box [data-field="secondary-icon"]') ||
        target.matches('.license-box [contenteditable="true"]') ||
        target.closest('.license-box [contenteditable="true"]')) {

        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData('text/plain');
        document.execCommand('insertText', false, text);
    }
});

// 定期刷新预览 (每 60 秒)
setInterval(() => {
    const imgs = document.querySelectorAll('.img-preview');
    imgs.forEach(img => {
        const box = img.closest('.image-block-box');
        const nameField = box.querySelector('[data-field="name"]');
        const url = nameField ? nameField.textContent.trim() : '';
        if (url && (url.startsWith('http') || url.startsWith('//'))) {
            const sep = url.includes('?') ? '&' : '?';
            const newSrc = url + sep + "t=" + Date.now();
            if (img.src !== newSrc) {
                img.src = newSrc;
            }
        }
    });
}, 60000);

window.addEventListener("load", function () {
    refreshAllImgs();
})