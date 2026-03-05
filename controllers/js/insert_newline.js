(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
    if (comp) {
        var p = document.createElement('p');
        p.innerHTML = '<br>';
        comp.parentNode.insertBefore(p, comp.nextSibling);

        var range = document.createRange();
        range.selectNodeContents(p);
        range.collapse(true);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }
})();