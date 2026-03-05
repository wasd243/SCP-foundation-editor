(function () {
    try {
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint(__POS_X__, __POS_Y__);
        var comp = null;

        if (el) {
            comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box');
        }

        if (!comp) {
            var sel = window.getSelection();
            if (sel.rangeCount > 0) {
                var range = sel.getRangeAt(0);
                var node = range.startContainer;
                if (node.nodeType === 3) node = node.parentNode;
                if (node) comp = node.closest('.scp-component');
            }
        }

        var divBox = document.createElement('div');
        divBox.className = 'scp-component raisa-box';
        divBox.setAttribute('data-type', 'raisa-notice');
        divBox.setAttribute('contenteditable', 'false');
        divBox.style.cssText = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5; position: relative; clear: both;";

        var divContent = document.createElement('div');
        divContent.className = 'raisa-content';
        divContent.setAttribute('contenteditable', 'true');

        var centerDiv = document.createElement('div');
        centerDiv.style.textAlign = 'center';
        centerDiv.className = 'raisa-inner';

        var titleSpan = document.createElement('span');
        titleSpan.style.fontSize = 'larger';
        var strong = document.createElement('strong');
        strong.innerText = '基金会记录与信息安全管理部的通知';
        titleSpan.appendChild(strong);

        centerDiv.appendChild(titleSpan);
        centerDiv.appendChild(document.createElement('br'));
        centerDiv.appendChild(document.createElement('br'));

        centerDiv.appendChild(document.createTextNode('通知在此'));
        centerDiv.appendChild(document.createElement('br'));
        centerDiv.appendChild(document.createElement('br'));
        centerDiv.appendChild(document.createTextNode('— Maria Jones，RAISA主管'));

        divContent.appendChild(centerDiv);
        divBox.appendChild(divContent);

        if (comp) {
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {
                comp.parentNode.replaceChild(divBox, comp);
            } else {
                comp.parentNode.insertBefore(divBox, comp.nextSibling);
            }
        } else {
            if (editor) { editor.appendChild(divBox); }
        }

        var br = document.createElement('br');
        if (divBox.nextSibling) { divBox.parentNode.insertBefore(br, divBox.nextSibling); }
        else { divBox.parentNode.appendChild(br); }
    } catch (e) { console.error("Error applying RAISA notice:", e); }
})();