(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
    if (comp) {
        function isIgnorable(node) {
            if (!node) return false;
            if (node.tagName === 'BR') return true;
            if (node.tagName === 'P' && node.innerText.trim() === '') return true;
            return false;
        }

        if (comp.classList.contains('half-width')) {
            var next = comp.nextElementSibling;
            while (next && isIgnorable(next)) {
                next = next.nextElementSibling;
            }
            if (next && next.classList.contains('half-width')) {
                comp = next;
            }
        }
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