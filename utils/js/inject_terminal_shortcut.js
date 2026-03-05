(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component') : null;
    var type = comp ? comp.getAttribute('data-type') : null;

    // 原生 CSS 写在反引号里，不需要任何转义！
    var cssContent = `
.danke{
    padding: 5px 5px 5px 15px;
    margin-bottom:10px;
    font-family: 'Courier New', monospace;
    font-size: 1.1em; 
}
.agent{
    background-color:#000000;
    border: 3px solid #55AA55;
    color: #77CC77;
}
.site{
    background-color:#222200;
    border: 3px solid #AAAA55;
    color: #DDDD77;
}`;

    var divHtml = `<div class="div-header" contenteditable="true">DIV: class="danke agent"</div><div class="div-content" contenteditable="true">| 细节<br>| 细节<br>| 细节<br>| 细节<br>| 细节<br><br>文字 文字 文字<br>更多文字<br><br>更多<br><br>以及更多<br><br>甚至还有更多要记录的文字</div>`;

    function createCssEl() {
        var box = document.createElement('div');
        box.className = 'scp-component css-box';
        box.setAttribute('data-type', 'css-module');
        box.setAttribute('contenteditable', 'false');
        box.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
        return box;
    }

    function createDivEl() {
        var divBox = document.createElement('div');
        divBox.className = 'scp-component div-box';
        divBox.setAttribute('data-type', 'div-block');
        divBox.setAttribute('contenteditable', 'false');
        divBox.innerHTML = divHtml;
        return divBox;
    }

    function hasTerminalCss() {
        var css = document.querySelectorAll('.css-box .css-content');
        for (var i = 0; i < css.length; i++) {
            if (css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
        }
        return false;
    }

    if (type === 'css-module') {
        comp.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
        var next = comp.nextElementSibling;
        var needDiv = true;
        if (next && next.classList.contains('div-box')) {
            var header = next.querySelector('.div-header');
            if (header && (header.innerText.indexOf('danke') !== -1 || header.innerText.indexOf('agent') !== -1)) {
                needDiv = false;
            }
        }
        if (needDiv) { comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }
    } else if (type === 'div-block') {
        var newDiv = createDivEl();
        comp.parentNode.replaceChild(newDiv, comp);
        if (!hasTerminalCss()) { editor.insertBefore(createCssEl(), editor.firstChild); }
    } else {
        if (!hasTerminalCss()) { editor.insertBefore(createCssEl(), editor.firstChild); }
        if (comp) { comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }
        else { editor.appendChild(createDivEl()); }
    }

    if (typeof updateTerminalStyle === 'function') updateTerminalStyle();
})();