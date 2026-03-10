function updateBasaltDocLayout() {
    var wrappers = document.querySelectorAll('.basalt-doc-wrapper');
    for (var i = 0; i < wrappers.length; i++) {
        var el = wrappers[i];
        var isHalf = false;

        function isIgnorable(node) {
            if (!node) return false;
            if (node.tagName === 'BR') return true;
            if (node.tagName === 'P' && node.innerText.trim() === '') return true;
            return false;
        }

        var next = el.nextElementSibling;
        var nextBetweens = [];
        while (next && isIgnorable(next)) {
            nextBetweens.push(next);
            next = next.nextElementSibling;
        }
        if (next && next.classList.contains('basalt-doc-wrapper')) {
            isHalf = true;
            nextBetweens.forEach(function (n) { n.style.display = 'none'; });
        } else {
            nextBetweens.forEach(function (n) { n.style.display = ''; });
        }

        var prev = el.previousElementSibling;
        while (prev && isIgnorable(prev)) {
            prev = prev.previousElementSibling;
        }
        if (prev && prev.classList.contains('basalt-doc-wrapper')) {
            isHalf = true;
        }

        if (isHalf) {
            el.classList.add('half-width');
            el.classList.remove('full-width');
        } else {
            el.classList.add('full-width');
            el.classList.remove('half-width');
        }
    }
}