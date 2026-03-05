(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component') : null;

    var divBox = document.createElement('div');
    divBox.className = 'scp-component div-box';
    divBox.setAttribute('data-type', 'div-block');
    divBox.setAttribute('contenteditable', 'false');
    divBox.style.cssText = 'position: relative; clear: both;';

    var divHeader = document.createElement('div');
    divHeader.className = 'div-header';
    divHeader.setAttribute('contenteditable', 'true');
    divHeader.setAttribute('onclick', 'toggleDiv(this)');
    divHeader.style.cssText = '';
    divHeader.title = '点击折叠/展开';
    divHeader.textContent = 'DIV: class="blockquote"';
    divBox.appendChild(divHeader);

    var divContent = document.createElement('div');
    divContent.className = 'div-content';
    divContent.setAttribute('contenteditable', 'true');
    divContent.innerHTML = `
        <div style="text-align:center;"><b>视频记录</b></div>
        <div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>
        <p><b>日期：</b></p>
        <p><b>笔记：</b></p>
        <div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>
        <p>[记录开始]</p>
        <p><b>时间：</b>事件</p>
        <p><b>时间：</b>事件</p>
        <p><b>时间：</b>事件</p>
        <div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>
        <p>[记录结束]</p>`;
    divBox.appendChild(divContent);

    if (comp) {
        if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {
            comp.parentNode.replaceChild(divBox, comp);
        } else { comp.parentNode.insertBefore(divBox, comp.nextSibling); }
    } else { editor.appendChild(divBox); }

    var br = document.createElement('br');
    if (divBox.nextSibling) { divBox.parentNode.insertBefore(br, divBox.nextSibling); }
    else { divBox.parentNode.appendChild(br); }
})();