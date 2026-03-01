(function (cls) {
    var editor = document.getElementById('editor-root');
    var sel = window.getSelection();
    var range = (sel.rangeCount > 0) ? sel.getRangeAt(0) : null;
    var lb = editor.querySelector('.license-box');

    var box = document.createElement('div');
    var base_cls = cls.split(' ')[0];
    if (cls.indexOf(' ') !== -1) {
        var parts = cls.split(' ');
        box.className = 'scp-component div-box basalt-div basalt-' + parts[0] + '-box ' + parts[1];
    } else {
        box.className = 'scp-component div-box basalt-div basalt-' + cls + '-box';
    }
    if (base_cls === 'document' || base_cls === 'darkdocument') {
        box.className += ' basalt-doc-wrapper';
    }
    if (base_cls.indexOf('_memo') !== -1) {
        box.className += ' basalt-memo-box';
    }
    box.setAttribute('data-type', 'div-block');
    box.setAttribute('data-class', cls);
    box.setAttribute('contenteditable', 'false');

    var header = document.createElement('div');
    header.className = 'div-header';
    header.setAttribute('contenteditable', 'false');
    header.innerText = '[[div class="' + cls + '"]]';
    box.appendChild(header);

    var content = document.createElement('div');
    content.className = 'div-content';
    content.setAttribute('contenteditable', 'true');
    // __CONTENT__ 将会被 Python 替换为安全的字符串变量
    content.innerHTML = '<p>' + __CONTENT__ + '</p>';
    box.appendChild(content);

    if (range && editor.contains(range.startContainer)) {
        var isAfterLb = false;
        if (lb) {
            if (lb.contains(range.startContainer) || (range.startContainer === editor && range.startOffset >= Array.from(editor.childNodes).indexOf(lb))) {
                isAfterLb = true;
            }
        }
        if (isAfterLb) { editor.insertBefore(box, lb); }
        else { range.collapse(false); range.insertNode(box); }
    } else {
        // 坐标占位符替换
        var el = document.elementFromPoint(__POS_X__, __POS_Y__);
        var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

        if (comp) {
            if (comp.classList.contains('license-box')) { comp.parentNode.insertBefore(box, comp); }
            else { comp.parentNode.insertBefore(box, comp.nextSibling); }
        } else {
            if (lb) { editor.insertBefore(box, lb); }
            else { editor.appendChild(box); }
        }
    }
    var br = document.createElement('br');
    box.parentNode.insertBefore(br, box.nextSibling);
    if (typeof updateBasaltDocLayout === 'function') { updateBasaltDocLayout(); }
})(__CLASS_NAME__);