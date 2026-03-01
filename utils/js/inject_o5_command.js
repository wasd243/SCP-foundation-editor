(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

    var divBox = document.createElement('div');
    divBox.className = 'scp-component o5-box';
    divBox.setAttribute('data-type', 'o5-command');
    divBox.setAttribute('contenteditable', 'false');

    var style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;";
    divBox.style.cssText = style + " position: relative; clear: both;";

    var divContent = document.createElement('div');
    divContent.className = 'o5-content';
    divContent.setAttribute('contenteditable', 'true');
    divContent.style.paddingTop = '80px';
    divContent.style.paddingBottom = '40px';

    var centerDiv = document.createElement('div');
    centerDiv.style.textAlign = 'center';
    centerDiv.className = 'o5-center-block';

    var h2 = document.createElement('h2');
    h2.className = 'o5-h2';
    h2.style.margin = '0';
    var span1 = document.createElement('span');
    span1.style.color = 'black';
    var strong1 = document.createElement('strong');
    strong1.textContent = '根据监督者议会的命令';
    span1.appendChild(strong1);
    h2.appendChild(span1);
    centerDiv.appendChild(h2);

    var p2 = document.createElement('div');
    p2.className = 'o5-p';
    var span2 = document.createElement('span');
    span2.style.color = 'black';
    span2.textContent = '以下文件为X/XXXX级机密。禁止未经授权的访问。';
    p2.appendChild(span2);
    centerDiv.appendChild(p2);

    divContent.appendChild(centerDiv);

    var h1 = document.createElement('h1');
    h1.className = 'o5-h1';
    h1.style.textAlign = 'center';
    var span3 = document.createElement('span');
    span3.style.color = 'black';
    var strong3 = document.createElement('strong');
    strong3.textContent = 'XXXX';
    span3.appendChild(strong3);
    h1.appendChild(span3);
    divContent.appendChild(h1);

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