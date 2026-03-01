(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component') : null;

    var box = document.createElement('div');
    box.className = 'scp-component login-logout-box';
    box.setAttribute('data-type', 'login-logout');
    box.setAttribute('contenteditable', 'false');
    box.style.cssText = 'border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;';

    var tbl = document.createElement('table');
    tbl.className = 'login-form-table';
    tbl.setAttribute('contenteditable', 'false');
    tbl.style.cssText = 'margin:0.5em auto; border-collapse:collapse;';

    var tr1 = document.createElement('tr');
    var td1a = document.createElement('td');
    td1a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
    td1a.setAttribute('contenteditable', 'false');
    td1a.textContent = 'ID';
    var td1b = document.createElement('td');
    var idInput = document.createElement('span');
    idInput.className = 'login-id-value';
    idInput.setAttribute('contenteditable', 'true');
    idInput.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;';
    idInput.textContent = '你的ID';
    td1b.appendChild(idInput);
    tr1.appendChild(td1a); tr1.appendChild(td1b);

    var tr2 = document.createElement('tr');
    var td2a = document.createElement('td');
    td2a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
    td2a.setAttribute('contenteditable', 'false');
    td2a.textContent = '密码';
    var td2b = document.createElement('td');
    var pwSpan = document.createElement('span');
    pwSpan.setAttribute('contenteditable', 'false');
    pwSpan.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;';
    pwSpan.textContent = '・・・・・・・・';
    td2b.appendChild(pwSpan);
    tr2.appendChild(td2a); tr2.appendChild(td2b);

    var tr3 = document.createElement('tr');
    var td3a = document.createElement('td');
    td3a.setAttribute('contenteditable', 'false');
    var td3b = document.createElement('td');
    td3b.style.textAlign = 'center';
    td3b.setAttribute('contenteditable', 'false');
    var btn = document.createElement('button');
    btn.setAttribute('contenteditable', 'false');
    btn.style.cssText = 'padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;';
    btn.textContent = '登入';
    td3b.appendChild(btn);
    tr3.appendChild(td3a); tr3.appendChild(td3b);

    tbl.appendChild(tr1); tbl.appendChild(tr2); tbl.appendChild(tr3);
    box.appendChild(tbl);

    var sep = document.createElement('hr');
    sep.setAttribute('contenteditable', 'false');
    sep.style.cssText = 'border:none; border-top:1px solid #ccc; margin:6px 0;';
    box.appendChild(sep);

    var lbl = document.createElement('div');
    lbl.setAttribute('contenteditable', 'false');
    lbl.style.cssText = 'font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;';
    lbl.textContent = '[登入]↔[登出] 折叠内容';
    box.appendChild(lbl);

    var content = document.createElement('div');
    content.className = 'login-collapsible-content';
    content.setAttribute('contenteditable', 'true');
    content.style.cssText = 'min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;';
    content.innerHTML = '<p>文字</p>';
    box.appendChild(content);

    if (comp) { comp.parentNode.insertBefore(box, comp.nextSibling); }
    else { editor.appendChild(box); }

    var br = document.createElement('br');
    box.parentNode.insertBefore(br, box.nextSibling);
})();