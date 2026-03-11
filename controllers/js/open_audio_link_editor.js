(function () {
    if (window._currentAudioLink) {
        var container = window._currentAudioLink.closest('.html5player-box');
        if (container) {
            // __NEW_URL__ 会被 Python 替换为安全的字符串，例如 "https://..."
            var newUrl = __NEW_URL__;

            var hiddenSpan = container.querySelector('.html5player-url');
            if (hiddenSpan) hiddenSpan.innerText = newUrl;

            var audioEl = container.querySelector('audio');
            if (audioEl) {
                var sources = audioEl.querySelectorAll('source');
                sources.forEach(function (s) { s.src = newUrl; });
                audioEl.load();
            }
        }
    }
})();