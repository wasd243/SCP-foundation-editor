use serde_json::Value;

pub(super) fn sanitize_data_editor_no_resize(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "data-editor-no-resize" {
                        None
                    } else {
                        Some((key, sanitize_data_editor_no_resize(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(sanitize_data_editor_no_resize)
                .collect(),
        ),
        _ => value,
    }
}
