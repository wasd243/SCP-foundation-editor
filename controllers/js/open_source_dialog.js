(function () {
    var max_attempts = 50;
    var attempts = 0;
    var timer = setInterval(function () {
        if (window.editorInstance) {
            clearInterval(timer);
            var view = window.editorInstance;
            var new_doc = __SAFE_CONTENT__;
            var current_doc = view.state.doc.toString();
            if (current_doc !== new_doc) {
                view.dispatch({
                    changes: {from: 0, to: view.state.doc.length, insert: new_doc}
                });
            }
        } else if (attempts >= max_attempts) {
            clearInterval(timer);
        }
        attempts++;
    }, 50);
})();
