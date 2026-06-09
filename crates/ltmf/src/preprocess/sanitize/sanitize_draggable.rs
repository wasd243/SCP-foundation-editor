use serde_json::Value;

pub(super) fn sanitize_draggable(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "draggable" {
                        None
                    } else {
                        Some((key, sanitize_draggable(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.into_iter().map(sanitize_draggable).collect()),
        _ => value,
    }
}
