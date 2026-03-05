function updateBasaltDocLayout() {
    var wrappers = document.querySelectorAll('.basalt-doc-wrapper');
    for (var i = 0; i < wrappers.length; i++) {
        var el = wrappers[i];
        var isHalf = false;

        var next = el.nextElementSibling;
        if (next && next.classList.contains('basalt-doc-wrapper')) {
            isHalf = true;
        }

        var prev = el.previousElementSibling;
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