(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box') : null;

    var divBox = document.createElement('div');
    divBox.className = 'scp-component class-warning-box';
    divBox.setAttribute('data-type', 'class-warning');
    divBox.setAttribute('contenteditable', 'false');

    var style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2); margin: 10px auto; width: fit-content;";
    divBox.style.cssText = style + " position: relative; clear: both;";

    var divContent = document.createElement('div');
    divContent.className = 'class-warning-content';
    divContent.setAttribute('contenteditable', 'true');

    var centerDiv = document.createElement('div');
    centerDiv.style.textAlign = 'center';
    centerDiv.className = 'class-warning-inner';

    var span1 = document.createElement('span');
    span1.style.color = 'rgb(255, 92, 72)';
    var span2 = document.createElement('span');
    span2.style.fontSize = '150%';
    var strong1 = document.createElement('strong');
    strong1.textContent = '警告：下列文件为#/XXXX级机密';
    span2.appendChild(strong1);
    span1.appendChild(span2);
    centerDiv.appendChild(span1);

    var hr = document.createElement('hr');
    hr.className = 'class-warning-hr';
    hr.style.border = 'none';
    hr.style.borderTop = '1px solid #777';
    hr.style.margin = '10px 0';
    centerDiv.appendChild(hr);

    var span3 = document.createElement('span');
    span3.style.fontSize = 'larger';
    var strong2 = document.createElement('strong');
    strong2.textContent = '无#/XXXX级权限下访问将被记录并立即处以纪律处分。';
    span3.appendChild(strong2);
    centerDiv.appendChild(span3);

    divContent.appendChild(centerDiv);
    divBox.appendChild(divContent);

    if (comp) {
        if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {
            comp.parentNode.replaceChild(divBox, comp);
        } else {
            comp.parentNode.insertBefore(divBox, comp.nextSibling);
        }
    } else {
        editor.appendChild(divBox);
    }

    var br = document.createElement('br');
    if (divBox.nextSibling) { divBox.parentNode.insertBefore(br, divBox.nextSibling); }
    else { divBox.parentNode.appendChild(br); }
})();