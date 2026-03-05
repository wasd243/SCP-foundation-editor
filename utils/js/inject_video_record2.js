(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component') : null;

    var divBox = document.createElement('div');
    divBox.className = 'scp-component div-box';
    divBox.setAttribute('data-type', 'div-block');
    divBox.setAttribute('contenteditable', 'false');
    divBox.style.cssText = 'border-radius: 10px; margin: 10px; position: relative; clear: both;';

    var divHeader = document.createElement('div');
    divHeader.className = 'div-header';
    divHeader.setAttribute('contenteditable', 'true');
    divHeader.setAttribute('onclick', 'toggleDiv(this)');
    divHeader.title = '点击折叠/展开';
    divHeader.textContent = 'DIV: class="blockquote" style="border-radius: 10px; margin: 10px"';
    divBox.appendChild(divHeader);

    var divContent = document.createElement('div');
    divContent.className = 'div-content';
    divContent.setAttribute('contenteditable', 'true');
    divContent.innerHTML = `
        <p><b>视频日志记录</b></p>
        <p><b>日期：</b>可选</p>
        <p><b>探索队伍：</b>队伍名称 - 可选</p>
        <p><b>目标：</b>区域/异常 - 可选</p>
        <p><b>领队：</b>可选</p>
        <p><b>小队成员：</b>可选</p>
        <div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>
        <p>[记录开始]</p>
        <p><b>人物A：</b>对白</p>
        <p><b>人物B：</b>对白</p>
        <p><i>事件发生</i></p>
        <p><b>人物A：</b>对白</p>
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