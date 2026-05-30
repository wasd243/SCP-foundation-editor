use serde_json::Value;

pub fn sanitize_unused_img_attrs(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "imageAttributes" {
                        None
                    } else {
                        Some((key, sanitize_unused_img_attrs(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(sanitize_unused_img_attrs)
                .collect(),
        ),
        _ => value,
    }
}
