use serde_json::Value;

pub fn sanitize_contenteditable(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "contenteditable" {
                        None
                    } else {
                        Some((key, sanitize_contenteditable(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => {
            Value::Array(values.into_iter().map(sanitize_contenteditable).collect())
        }
        _ => value,
    }
}
