function insertLicenseBox() {
    var editor = document.getElementById('editor-root');
    var html = '<div class="scp-component license-box open" data-type="license" data-original="false" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)<button class="btn-license-original" onclick="toggleLicenseOriginal(this, event)" title="原创：生成|lang=CN，并取消|translator">原创</button></div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true"></span></div><div class="license-field-row license-translator-row"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true"></span></div><hr><div class="extra-files-container"></div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>';
    editor.insertAdjacentHTML('beforeend', html);
}

function toggleLicenseOriginal(btn, event) {
    if (event) { event.stopPropagation(); event.preventDefault(); }
    var box = btn.closest('.license-box');
    var isOriginal = box.getAttribute('data-original') === 'true';
    if (isOriginal) {
        // 关闭原创模式
        box.setAttribute('data-original', 'false');
        btn.classList.remove('active');
        var transRow = box.querySelector('.license-translator-row');
        if (transRow) transRow.classList.remove('disabled');
    } else {
        // 开启原创模式
        box.setAttribute('data-original', 'true');
        btn.classList.add('active');
        var transRow = box.querySelector('.license-translator-row');
        if (transRow) {
            transRow.classList.add('disabled');
            var transField = transRow.querySelector('[data-field="translator"]');
            if (transField) transField.innerText = '';
        }
    }
}