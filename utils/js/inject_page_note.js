(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

    var box = document.createElement('div');
    box.className = 'scp-component page-note-box';
    box.setAttribute('data-type', 'page-note');
    box.setAttribute('contenteditable', 'false');
    box.style.cssText = 'display:block; overflow:hidden; font-family:"Monotype Corsiva","Bradley Hand ITC",sans-serif; background-attachment:scroll; background-image:linear-gradient(to top,rgb(202,219,228) 0%,rgb(231,233,220) 8%); background-position:0px 8px; background-repeat:repeat; background-size:100% 20px; border:1px solid #CCC; border-radius:10px; padding:10px; margin-bottom:10px; box-shadow:0px 1px 3px rgba(0,0,0,0.2); position:relative; clear:both;';

    var label = document.createElement('div');
    label.className = 'page-note-label';
    label.setAttribute('contenteditable', 'false');
    label.style.cssText = 'font-size:10px;color:#aaa;text-align:right;margin-bottom:2px;';
    label.textContent = '便签纸';
    box.appendChild(label);

    var content = document.createElement('div');
    content.className = 'page-note-content';
    content.setAttribute('contenteditable', 'true');
    content.style.cssText = "font-family:'Monotype Corsiva','Bradley Hand ITC',sans-serif;line-height:20px;";
    content.innerHTML = '<p>正文在此。</p><p><br></p><p>就像这样。</p>';
    box.appendChild(content);

    if (comp) {
        if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {
            comp.parentNode.replaceChild(box, comp);
        } else { comp.parentNode.insertBefore(box, comp.nextSibling); }
    } else {
        if (editor) { editor.appendChild(box); }
    }

    var br = document.createElement('br');
    if (box.nextSibling) { box.parentNode.insertBefore(br, box.nextSibling); }
    else { box.parentNode.appendChild(br); }
})();