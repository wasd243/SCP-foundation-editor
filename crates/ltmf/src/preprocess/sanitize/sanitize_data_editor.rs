use serde_json::Value;

// Sanitize some unuseful data-editor when export to wikitext
use crate::preprocess::sanitize::sanitize_data_editor::no_resize::sanitize_data_editor_no_resize;

pub(super) mod no_resize;

pub(super) fn sanitize_data_editor(value: Value) -> Value {
    sanitize_data_editor_no_resize(value)
}
