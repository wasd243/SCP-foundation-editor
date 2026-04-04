if (window.editorInstance) {
    var view = window.editorInstance;
    var current_doc = view.state.doc.toString();
    var new_doc = __SAFE_CONTENT__;
    if (current_doc !== new_doc) {
        view.dispatch({
            changes: { from: 0, to: view.state.doc.length, insert: new_doc }
        });
    }
}