(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component') : null;
    var type = comp ? comp.getAttribute('data-type') : null;

    var cssContent = `
div.terminal{
    border: 1px solid black;
    border: solid 3px #BBBBBB;
    border-radius: 16px;
    background-color: #000000;
    background-image: radial-gradient(ellipse 1000% 100% at 50% 90%, transparent, #121);
    background-position: center;
    display: block;
    box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5);
    overflow:hidden;
}
div.terminal blockquote {
    background-color: black;
    border: double 3px #80FF80;
    color: #80FF80;
}
div.scanline{
    margin-top: -40%;
    width: 100%;
    height: 60px;
    position: relative;
    pointer-events: none;
    -webkit-animation: scan 12s linear 0s infinite; 
    animation: scan 12s linear 0s infinite; 
    background: linear-gradient(to bottom, rgba(56, 112, 82,0), rgba(56, 112, 82,0.1)) !important;
}
div.text{
    color: rgba(128,255,128,0.8);
    padding-left: 2em;
    padding-top: 40%;
    font-family: 'Courier New', monospace;
    font-size: 1.2em;
}
@keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} 
}
div.text a, div.text a.newpage {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a:hover {
    color: #131;
    text-decoration: underline;
    background-color: #80FF80;
    padding: 1px;
}
div.text a:hover::before{
    content: "> ";
}`;

    var divHtml = `<div class="scp-component div-box terminal" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="terminal"</div><div class="div-content" contenteditable="true"><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="scanline"</div><div class="div-content" contenteditable="true"></div></div><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="text"</div><div class="div-content" contenteditable="true"><div style="text-align: center;"><span style="font-size: 150%;"><u>终端 #001</u></span><br><p><br></p><p><br></p><span class="terminal-hr">------</span><br>欢迎，用户<br><span class="terminal-hr">------</span><br></div><p><br></p><p><br></p><p><br></p><blockquote>终端内部的链接会在鼠标移过时显示“&gt;”。<br><a href="http://www.baidu.com">就像这样</a></blockquote><br>谢谢你查看我的格式！<br><p><br></p><p><br></p></div></div></div></div>`;

    function createCssEl() {
        var box = document.createElement('div');
        box.className = 'scp-component css-box';
        box.setAttribute('data-type', 'css-module');
        box.setAttribute('contenteditable', 'false');
        box.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
        return box;
    }

    function createDivEl() {
        return document.createRange().createContextualFragment(divHtml);
    }

    function hasTerminalCss() {
        var css = document.querySelectorAll('.css-box .css-content');
        for (var i = 0; i < css.length; i++) {
            if (css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
        }
        return false;
    }

    if (type === 'css-module') {
        comp.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
        var next = comp.nextElementSibling;
        var needDiv = true;
        if (next && next.classList.contains('div-box')) {
            var header = next.querySelector('.div-header');
            if (header && header.innerText.indexOf('terminal') !== -1) { needDiv = false; }
        }
        if (needDiv) { comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }
    } else if (type === 'div-block') {
        var newDiv = createDivEl();
        comp.parentNode.replaceChild(newDiv, comp);
        if (!hasTerminalCss()) { editor.insertBefore(createCssEl(), editor.firstChild); }
    } else {
        if (!hasTerminalCss()) { editor.insertBefore(createCssEl(), editor.firstChild); }
        if (comp) {
            var newDiv = createDivEl();
            comp.parentNode.insertBefore(newDiv, comp.nextSibling);
        } else { editor.appendChild(createDivEl()); }
    }

    if (typeof updateTerminalStyle === 'function') updateTerminalStyle();
})();